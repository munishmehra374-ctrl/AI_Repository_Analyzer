from __future__ import annotations

import re

from app.retrieval.context_optimizer import ContextOptimizer
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.rrf import ReciprocalRankFusion


class RetrievalService:
    """
    Orchestrates the complete retrieval pipeline.
    """

    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        rrf: ReciprocalRankFusion,
        reranker: CrossEncoderReranker,
        context_optimizer: ContextOptimizer,
    ) -> None:

        self._hybrid_retriever = hybrid_retriever
        self._rrf = rrf
        self._reranker = reranker
        self._context_optimizer = context_optimizer

    # ------------------------------------------------------------------ #
    # Identifier Detection
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_identifier(
        question: str,
    ) -> str | None:
        """
        Extract an explicitly mentioned function/class identifier.

        Example:
            "Explain index_repository()"
            -> "index_repository"
        """

        match = re.search(
            r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            question,
        )

        if match:
            return match.group(1)

        match = re.search(
            r"`([A-Za-z_][A-Za-z0-9_]*)`",
            question,
        )

        if match:
            return match.group(1)

        return None

    # ------------------------------------------------------------------ #
    # Chunk Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _get_metadata_value(
        chunk,
        key: str,
        default="",
    ):
        """
        Get metadata from either:

        1. LangChain Document
        2. Dictionary chunk
        """

        if hasattr(chunk, "metadata"):

            return chunk.metadata.get(
                key,
                default,
            )

        return chunk.get(
            key,
            default,
        )

    @staticmethod
    def _get_chunk_id(
        chunk,
    ):
        """
        Get chunk_id from either a LangChain Document
        or a dictionary chunk.
        """

        return RetrievalService._get_metadata_value(
            chunk,
            "chunk_id",
            None,
        )

    @staticmethod
    def _find_exact_identifier(
        chunks,
        identifier: str | None,
    ):
        """
        Find a chunk whose name or qualified_name exactly
        matches the requested identifier.

        Supports both:
        - LangChain Document objects
        - Dictionary chunks
        """

        if not identifier:
            return None

        identifier_lower = identifier.lower()

        for chunk in chunks:

            name = str(
                RetrievalService._get_metadata_value(
                    chunk,
                    "name",
                    "",
                )
            ).lower()

            qualified_name = str(
                RetrievalService._get_metadata_value(
                    chunk,
                    "qualified_name",
                    "",
                )
            ).lower()

            if (
                name == identifier_lower
                or qualified_name == identifier_lower
            ):
                return chunk

        return None

    # ------------------------------------------------------------------ #
    # Move Exact Match To Front
    # ------------------------------------------------------------------ #

    @staticmethod
    def _move_exact_match_to_front(
        chunks,
        exact_chunk_id,
    ):
        """
        Move the exact requested chunk to the beginning
        of a list.

        Works with dictionary chunks.
        """

        if not exact_chunk_id:
            return chunks

        exact_chunk = None
        remaining_chunks = []

        for chunk in chunks:

            chunk_id = (
                RetrievalService._get_chunk_id(
                    chunk
                )
            )

            if chunk_id == exact_chunk_id:

                exact_chunk = chunk

            else:

                remaining_chunks.append(chunk)

        if exact_chunk is None:
            return chunks

        return [
            exact_chunk
        ] + remaining_chunks

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def retrieve(
        self,
        question: str,
    ) -> str:

        print(
            "\n========== RETRIEVAL SERVICE =========="
        )

        print(
            "Question:",
            question,
        )

        # -----------------------------------------
        # Query Analysis
        # -----------------------------------------

        identifier = self._extract_identifier(
            question
        )

        print(
            "\n========== QUERY ANALYSIS =========="
        )

        print(
            "Detected Identifier:",
            identifier,
        )

        print(
            "====================================\n"
        )

        # -----------------------------------------
        # Step 1 : Hybrid Retrieval
        # -----------------------------------------

        results = self._hybrid_retriever.retrieve(
            query=question,
            vector_k=20,
            bm25_k=20,
        )

        vector_results = results[
            "vector_results"
        ]

        bm25_results = results[
            "bm25_results"
        ]

        print(
            f"\nVector Results : "
            f"{len(vector_results)}"
        )

        print(
            f"BM25 Results   : "
            f"{len(bm25_results)}"
        )

        # -----------------------------------------
        # Step 1A : Find Exact Identifier
        # -----------------------------------------

        exact_match = (
            self._find_exact_identifier(
                bm25_results,
                identifier,
            )
        )

        if exact_match is None:

            exact_match = (
                self._find_exact_identifier(
                    vector_results,
                    identifier,
                )
            )

        if exact_match:

            exact_chunk_id = (
                self._get_chunk_id(
                    exact_match
                )
            )

            print(
                "\n========== EXACT MATCH FOUND =========="
            )

            print(
                "Identifier:",
                identifier,
            )

            print(
                "Name:",
                self._get_metadata_value(
                    exact_match,
                    "name",
                ),
            )

            print(
                "File:",
                self._get_metadata_value(
                    exact_match,
                    "file_path",
                ),
            )

            print(
                "Type:",
                self._get_metadata_value(
                    exact_match,
                    "type",
                ),
            )

            print(
                "Chunk ID:",
                exact_chunk_id,
            )

            print(
                "=======================================\n"
            )

        else:

            exact_chunk_id = None

            print(
                "\n========== EXACT MATCH NOT FOUND =========="
            )

            print(
                "Identifier:",
                identifier,
            )

            print(
                "===========================================\n"
            )

        # -----------------------------------------
        # Step 2 : Reciprocal Rank Fusion
        # -----------------------------------------

        fused_results = self._rrf.fuse(
            vector_results=vector_results,
            bm25_results=bm25_results,
        )

        print(
            f"\nFused Results : "
            f"{len(fused_results)}"
        )

        # -----------------------------------------
        # Step 2A : Preserve Exact Match
        # -----------------------------------------

        if exact_chunk_id:

            fused_results = (
                self._move_exact_match_to_front(
                    fused_results,
                    exact_chunk_id,
                )
            )

        if fused_results:

            print(
                "\nFirst Fused Result:"
            )

            print(
                fused_results[0]
            )

        # -----------------------------------------
        # Step 3 : Cross Encoder Re-ranking
        # -----------------------------------------

        reranked_results = (
            self._reranker.rerank(
                query=question,
                chunks=fused_results,
                top_k=10,
            )
        )

        print(
            f"\nReranked Results : "
            f"{len(reranked_results)}"
        )

        # -----------------------------------------
        # Step 3A : Preserve Exact Match
        # -----------------------------------------

        if exact_chunk_id:

            reranked_results = (
                self._move_exact_match_to_front(
                    reranked_results,
                    exact_chunk_id,
                )
            )

        if reranked_results:

            print(
                "\nFirst Reranked Result:"
            )

            print(
                reranked_results[0]
            )


                    # -----------------------------------------
        # Step 4 : Context Optimization
        # -----------------------------------------

        optimized_context = (
            self._context_optimizer.optimize(
                reranked_results
            )
        )

        print(
            "\n========== OPTIMIZED CONTEXT DEBUG =========="
        )

        print(
            "Optimized chunk count:",
            len(optimized_context),
        )

        total_code_chars = 0

        for i, chunk in enumerate(
            optimized_context,
            start=1,
        ):

            code = self._get_metadata_value(
                chunk,
                "code",
                "",
            )

            print(
                f"Chunk {i}:",
                "name=",
                self._get_metadata_value(
                    chunk,
                    "name",
                    "",
                ),
                "| code length=",
                len(code),
            )

            total_code_chars += len(code)

        print(
            "TOTAL CODE CHARACTERS:",
            total_code_chars,
        )

        print(
            "=============================================\n"
        )

        # -----------------------------------------
        # Step 4A : Preserve Exact Match
        # -----------------------------------------

        if exact_chunk_id:

            optimized_context = (
                self._move_exact_match_to_front(
                    optimized_context,
                    exact_chunk_id,
                )
            )

        print(
            f"\nOptimized Chunks : "
            f"{len(optimized_context)}"
        )

        # -----------------------------------------
        # Step 5 : Build Structured Context
        # -----------------------------------------

        sections = []

        for index, chunk in enumerate(
            optimized_context,
            start=1,
        ):

            file_path = self._get_metadata_value(
                chunk,
                "file_path",
                "Unknown",
            )

            chunk_type = self._get_metadata_value(
                chunk,
                "type",
                "Unknown",
            )

            name = self._get_metadata_value(
                chunk,
                "name",
                "Unknown",
            )

            language = self._get_metadata_value(
                chunk,
                "language",
                "Unknown",
            )

            start_line = self._get_metadata_value(
                chunk,
                "start_line",
                "?",
            )

            end_line = self._get_metadata_value(
                chunk,
                "end_line",
                "?",
            )

            class_name = self._get_metadata_value(
                chunk,
                "class_name",
                None,
            )

            # At this point chunks should be dictionaries
            # because RRF converts Documents to dictionaries.

            code = self._get_metadata_value(
                chunk,
                "code",
                "",
            )

            section = f"""
File:
{file_path}

Type:
{chunk_type}

Name:
{name}

Class:
{class_name if class_name else "None"}

Language:
{language}

Lines:
{start_line} - {end_line}

Code:
{code}
"""

            sections.append(
                section
            )

        # -----------------------------------------
        # Step 6 : Final Context
        # -----------------------------------------

        if sections:

            context = "\n".join(
                sections
            )

        else:

            context = (
                "No relevant repository context "
                "was found."
            )

        print(
            "\n========== FINAL RETRIEVAL CONTEXT =========="
        )

        print(
            context[:5000]
        )

        print(
            "=============================================\n"
        )

        return context