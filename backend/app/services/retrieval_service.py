from __future__ import annotations

from app.knowledge.entity_resolver import EntityResolver
from app.retrieval.context_optimizer import ContextOptimizer
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.rrf import ReciprocalRankFusion


class RetrievalService:
    """
    Orchestrates the complete retrieval pipeline.

    Pipeline:

        Question
            ↓
        Entity Resolution
            ↓
        Hybrid Retrieval
            ↓
        Reciprocal Rank Fusion
            ↓
        Cross Encoder Re-ranking
            ↓
        Context Optimization
            ↓
        Structured Context
    """

    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        rrf: ReciprocalRankFusion,
        reranker: CrossEncoderReranker,
        context_optimizer: ContextOptimizer,
        entity_resolver: EntityResolver,
    ):
        self._hybrid_retriever = hybrid_retriever
        self._rrf = rrf
        self._reranker = reranker
        self._context_optimizer = context_optimizer
        self._entity_resolver = entity_resolver

    # ------------------------------------------------------------------
    # Chunk Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _get_metadata_value(
        chunk,
        key: str,
        default="",
    ):
        """
        Read metadata from either:

        1. LangChain Document
        2. Dictionary chunk
        """

        if hasattr(chunk, "metadata"):

            return chunk.metadata.get(
                key,
                default,
            )

        if isinstance(chunk, dict):

            return chunk.get(
                key,
                default,
            )

        return default

    @staticmethod
    def _get_chunk_id(
        chunk,
    ):
        """
        Get chunk_id from a Document or dictionary.
        """

        return RetrievalService._get_metadata_value(
            chunk,
            "chunk_id",
            None,
        )

    @staticmethod
    def _find_exact_entity(
        chunks,
        entity_name: str | None,
    ):
        """
        Find a chunk whose repository entity name
        exactly matches the entity resolved from Neo4j.

        No hardcoded class/function names are used.
        """

        if not entity_name:
            return None

        target = (
            entity_name
            .strip()
            .lower()
        )

        for chunk in chunks:

            name = str(
                RetrievalService._get_metadata_value(
                    chunk,
                    "name",
                    "",
                )
            ).strip().lower()

            qualified_name = str(
                RetrievalService._get_metadata_value(
                    chunk,
                    "qualified_name",
                    "",
                )
            ).strip().lower()

            if (
                name == target
                or qualified_name == target
            ):

                return chunk

        return None

    @staticmethod
    def _mark_exact_entity(
        chunks,
        entity_name: str | None,
    ):
        """
        Mark chunks belonging to the resolved entity.

        This allows ContextOptimizer to prioritize
        the exact entity without hardcoding names.
        """

        if not entity_name:
            return chunks

        target = (
            entity_name
            .strip()
            .lower()
        )

        for chunk in chunks:

            name = str(
                RetrievalService._get_metadata_value(
                    chunk,
                    "name",
                    "",
                )
            ).strip().lower()

            qualified_name = str(
                RetrievalService._get_metadata_value(
                    chunk,
                    "qualified_name",
                    "",
                )
            ).strip().lower()

            chunk[
                "is_exact_identifier_match"
            ] = (
                name == target
                or qualified_name == target
            )

        return chunks

    @staticmethod
    def _move_exact_match_to_front(
        chunks,
        exact_chunk_id,
    ):
        """
        Move the exact entity chunk to the beginning.
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

                remaining_chunks.append(
                    chunk
                )

        if exact_chunk is None:
            return chunks

        return [
            exact_chunk
        ] + remaining_chunks

    def _ensure_exact_entity(
        self,
        chunks,
        exact_match,
        exact_chunk_id,
    ):
        """
        Ensure the resolved exact entity remains
        available in the candidate list.

        This is generic and does not hardcode
        any repository entity name.
        """

        if not exact_match or not exact_chunk_id:
            return chunks

        # ----------------------------------------------------------
        # Check whether the exact entity is already present
        # ----------------------------------------------------------

        for chunk in chunks:

            if (
                self._get_chunk_id(chunk)
                == exact_chunk_id
            ):
                return chunks

        # ----------------------------------------------------------
        # Exact entity was removed by a previous stage.
        # Restore it.
        # ----------------------------------------------------------

        exact_match = exact_match.copy()

        exact_match[
            "is_exact_identifier_match"
        ] = True

        return [
            exact_match,
            *chunks,
        ]

        # ------------------------------------------------------------------
    # Public Retrieval API
    # ------------------------------------------------------------------

    def retrieve(
    self,
    question: str,
    return_candidates: bool = False,
    repository_id: str | None = None,
    ) -> str:

        print(
            "\n========== RETRIEVAL SERVICE =========="
        )

        print(
            "Question:",
            question,
        )

        print(
           "Repository ID:",
            repository_id,
         )

        # ==============================================================
        # STEP 0 : ENTITY RESOLUTION
        # ==============================================================

        entity = self._entity_resolver.resolve(
            question
        )

        entity_type = entity.get(
            "type"
        )

        entity_name = entity.get(
            "name"
        )

        print(
            "\n========== ENTITY RESOLUTION =========="
        )

        print(
            "Entity Type:",
            entity_type,
        )

        print(
            "Entity Name:",
            entity_name,
        )

        print(
            "========================================\n"
        )

        # ==============================================================
        # STEP 1 : HYBRID RETRIEVAL
        # ==============================================================

        results = self._hybrid_retriever.retrieve(
                query=question,
                vector_k=20,
                bm25_k=20,
                entity_name=entity_name,
                repository_id=repository_id,
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

        # ==============================================================
        # STEP 1A : DEBUG RAW HYBRID RESULTS
        # ==============================================================

        print(
            "\n========== RAW HYBRID RESULTS =========="
        )

        print(
            "\n----- VECTOR RESULTS -----"
        )

        for i, chunk in enumerate(
            vector_results
        ):

            print(
                f"\nVECTOR RESULT {i}:"
            )

            print(
                "Name:",
                self._get_metadata_value(
                    chunk,
                    "name",
                    "",
                )
            )

            print(
                "Qualified:",
                self._get_metadata_value(
                    chunk,
                    "qualified_name",
                    "",
                )
            )

            print(
                "File:",
                self._get_metadata_value(
                    chunk,
                    "file_path",
                    "",
                )
            )

        print(
            "\n----- BM25 RESULTS -----"
        )

        for i, chunk in enumerate(
            bm25_results
        ):

            print(
                f"\nBM25 RESULT {i}:"
            )

            print(
                "Name:",
                self._get_metadata_value(
                    chunk,
                    "name",
                    "",
                )
            )

            print(
                "Qualified:",
                self._get_metadata_value(
                    chunk,
                    "qualified_name",
                    "",
                )
            )

            print(
                "File:",
                self._get_metadata_value(
                    chunk,
                    "file_path",
                    "",
                )
            )

            print(
                "BM25 Score:",
                self._get_metadata_value(
                    chunk,
                    "bm25_score",
                    "",
                )
            )

        print(
            "========================================\n"
        )

        # ==============================================================
        # STEP 1B : EXACT ENTITY MATCH
        # ==============================================================

        exact_match = None

        if entity_name:

            exact_match = (
                self._find_exact_entity(
                    bm25_results,
                    entity_name,
                )
            )

            if exact_match is None:

                exact_match = (
                    self._find_exact_entity(
                        vector_results,
                        entity_name,
                    )
                )

        exact_chunk_id = None

        if exact_match:

            exact_chunk_id = (
                self._get_chunk_id(
                    exact_match
                )
            )

            print(
                "\n========== EXACT ENTITY MATCH FOUND =========="
            )

            print(
                "Entity Type:",
                entity_type,
            )

            print(
                "Entity Name:",
                entity_name,
            )

            print(
                "Name:",
                self._get_metadata_value(
                    exact_match,
                    "name",
                    "",
                ),
            )

            print(
                "File:",
                self._get_metadata_value(
                    exact_match,
                    "file_path",
                    "",
                ),
            )

            print(
                "Type:",
                self._get_metadata_value(
                    exact_match,
                    "type",
                    "",
                ),
            )

            print(
                "Chunk ID:",
                exact_chunk_id,
            )

            print(
                "==============================================\n"
            )

        else:

            print(
                "\n========== EXACT ENTITY MATCH NOT FOUND =========="
            )

            print(
                "Entity Type:",
                entity_type,
            )

            print(
                "Entity Name:",
                entity_name,
            )

            print(
                "===================================================\n"
            )
        # ==============================================================
        # STEP 2 : RECIPROCAL RANK FUSION
        # ==============================================================

        fused_results = self._rrf.fuse(
            vector_results=vector_results,
            bm25_results=bm25_results,
        )

        print(f"\nFused Results : {len(fused_results)}")

        # Tag and preserve exact entity matches in RRF results
        fused_results = self._mark_exact_entity(fused_results, entity_name)

        if exact_chunk_id:
            fused_results = self._ensure_exact_entity(
                fused_results,
                exact_match,
                exact_chunk_id,
            )
            fused_results = self._move_exact_match_to_front(
                fused_results,
                exact_chunk_id,
            )

        if fused_results:
            print("\nFirst Fused Result:")
            print(fused_results[0])

        # ==============================================================
        # STEP 3 : CROSS ENCODER RE-RANKING
        # ==============================================================

        reranked_results = self._reranker.rerank(
            query=question,
            chunks=fused_results,
            top_k=20,
        )

        # Re-ensure exact match integrity post-reranking
        reranked_results = self._mark_exact_entity(reranked_results, entity_name)

        if exact_chunk_id:
            reranked_results = self._ensure_exact_entity(
                reranked_results,
                exact_match,
                exact_chunk_id,
            )
            reranked_results = self._mark_exact_entity(reranked_results, entity_name)
            reranked_results = self._move_exact_match_to_front(
                reranked_results,
                exact_chunk_id,
            )

        # ==============================================================
        # GLOBAL CONTEXT SELECTION CANDIDATES
        # ==============================================================

        if return_candidates:
            print("\n========== RETRIEVAL CANDIDATES ==========")
            print("Candidate count:", len(reranked_results))

            for index, chunk in enumerate(reranked_results, start=1):
                name_val = self._get_metadata_value(chunk, "name", "")
                file_val = self._get_metadata_value(chunk, "file_path", "")
                ce_score = self._get_metadata_value(chunk, "cross_encoder_score", 0.0)
                rrf_score = self._get_metadata_value(chunk, "rrf_score", 0.0)
                exact_match_flag = chunk.get("is_exact_identifier_match", False) or \
                                  self._get_metadata_value(chunk, "is_exact_identifier_match", False)

                # Standardize top-level dictionary keys for ContextSelectionService
                chunk["is_exact_identifier_match"] = exact_match_flag

                print(f"\nCandidate {index}")
                print("Name:", name_val)
                print("File:", file_val)
                print("Cross Encoder Score:", ce_score)
                print("RRF Score:", rrf_score)
                print("Exact Match:", exact_match_flag)

            print("===========================================\n")
            return reranked_results

        print(f"\nReranked Results : {len(reranked_results)}")

        if reranked_results:
            print("\nFirst Reranked Result:")
            print(reranked_results[0])

        # ==============================================================
        # STEP 4 : CONTEXT OPTIMIZATION
        # ==============================================================

        optimized_context = self._context_optimizer.optimize(
            chunks=reranked_results,
            query=question,
        )

        print("\n========== OPTIMIZED CONTEXT DEBUG ==========")
        print("Optimized chunk count:", len(optimized_context))

        total_code_chars = 0

        for i, chunk in enumerate(optimized_context, start=1):
            code = self._get_metadata_value(chunk, "code", "")
            chunk_name = self._get_metadata_value(chunk, "name", "")
            print(
                f"Chunk {i}: name= {chunk_name} | code length= {len(code)}"
            )
            total_code_chars += len(code)

        print("TOTAL CODE CHARACTERS:", total_code_chars)
        print("=============================================\n")

        # Preserve exact entity after optimization
        if exact_chunk_id:
            optimized_context = self._ensure_exact_entity(
                optimized_context,
                exact_match,
                exact_chunk_id,
            )
            optimized_context = self._mark_exact_entity(
                optimized_context,
                entity_name,
            )
            optimized_context = self._move_exact_match_to_front(
                optimized_context,
                exact_chunk_id,
            )

        print(f"\nOptimized Chunks : {len(optimized_context)}")

        # ==============================================================
        # STEP 5 : BUILD STRUCTURED CONTEXT
        # ==============================================================

        sections = []

        for index, chunk in enumerate(optimized_context, start=1):
            file_path = self._get_metadata_value(chunk, "file_path", "Unknown")
            chunk_type = self._get_metadata_value(chunk, "type", "Unknown")
            name = self._get_metadata_value(chunk, "name", "Unknown")
            language = self._get_metadata_value(chunk, "language", "Unknown")
            start_line = self._get_metadata_value(chunk, "start_line", "?")
            end_line = self._get_metadata_value(chunk, "end_line", "?")
            class_name = self._get_metadata_value(chunk, "class_name", None)
            code = self._get_metadata_value(chunk, "code", "")

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
            sections.append(section)

        # ==============================================================
        # STEP 6 : FINAL CONTEXT
        # ==============================================================

        if sections:
            context = "\n".join(sections)
        else:
            context = "No relevant repository context was found."

        print("\n========== FINAL RETRIEVAL CONTEXT ==========")
        print(context[:5000])
        print("=============================================\n")

        return context