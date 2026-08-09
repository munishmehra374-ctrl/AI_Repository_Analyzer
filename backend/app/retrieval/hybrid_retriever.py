from __future__ import annotations

import logging
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional

from app.retrieval.bm25_retriever import BM25Retriever
from app.vectorstore.retriever import RepositoryRetriever


logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Executes Vector Search and BM25 Search.

    Responsibilities
    ----------------
    - Execute vector search and BM25 search.
    - Detect explicit repository identifiers.
    - Find exact identifier matches.
    - Mark exact identifier matches.

    This class DOES NOT:
    - Merge results using RRF.
    - Perform cross-encoder re-ranking.
    - Optimize context.
    """

    def __init__(
        self,
        vector_retriever: RepositoryRetriever,
        bm25_retriever: BM25Retriever,
    ) -> None:

        self._vector_retriever = vector_retriever
        self._bm25_retriever = bm25_retriever

    # ==============================================================
    # Public API
    # ==============================================================

    def retrieve(
        self,
        query: str,
        vector_k: int = 10,
        bm25_k: int = 10,
    ) -> Dict[str, List]:

        if not query.strip():

            logger.warning("Empty query received.")

            return {
                "vector_results": [],
                "bm25_results": [],
            }

        if vector_k <= 0:
            raise ValueError(
                "vector_k must be greater than zero."
            )

        if bm25_k <= 0:
            raise ValueError(
                "bm25_k must be greater than zero."
            )

        identifier = self._extract_identifier(query)

        print("\n========== HYBRID RETRIEVAL ==========")
        print("Query:", query)
        print("Detected Identifier:", identifier)

        # ==========================================================
        # Normal Vector + BM25 Retrieval
        # ==========================================================

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:

            vector_future = executor.submit(
                self._vector_retriever.retrieve,
                query=query,
                top_k=vector_k,
            )

            bm25_future = executor.submit(
                self._bm25_retriever.retrieve,
                query=query,
                top_k=bm25_k,
            )

            vector_results = vector_future.result()
            bm25_results = bm25_future.result()

        # ==========================================================
        # Exact Identifier Search
        # ==========================================================

        if identifier:

            print(
                "\n========== EXACT IDENTIFIER SEARCH =========="
            )

            print(
                "Searching BM25 for:",
                identifier,
            )

            exact_results = self._bm25_retriever.retrieve(
                query=identifier,
                top_k=10,
            )

            exact_match = self._find_exact_identifier(
                exact_results,
                identifier,
            )

            if exact_match is not None:

                exact_match = exact_match.copy()

                exact_match[
                    "is_exact_identifier_match"
                ] = True

                exact_chunk_id = exact_match.get(
                    "chunk_id"
                )

                print(
                    "\nEXACT IDENTIFIER MATCH FOUND:",
                    identifier,
                )

                print(
                    "File:",
                    exact_match.get(
                        "file_path",
                        "",
                    ),
                )

                print(
                    "Name:",
                    exact_match.get(
                        "name",
                        "",
                    ),
                )

                # Put exact result first.
                bm25_results = [
                    exact_match
                ] + [
                    chunk
                    for chunk in bm25_results
                    if self._get_chunk_id(chunk)
                    != exact_chunk_id
                ]

            else:

                print(
                    "\nEXACT IDENTIFIER MATCH NOT FOUND:",
                    identifier,
                )

        # ==========================================================
        # Mark Exact Matches Already Present In Vector Results
        # ==========================================================

        if identifier:

            vector_results = self._mark_exact_matches(
                vector_results,
                identifier,
            )

        print(
            "\nVector Results:",
            len(vector_results),
        )

        print(
            "BM25 Results:",
            len(bm25_results),
        )

        if bm25_results:

            print(
                "\n===== FIRST BM25 RESULT ====="
            )

            print(
                self._debug_result(
                    bm25_results[0]
                )
            )

        print(
            "=====================================\n"
        )

        return {
            "vector_results": vector_results,
            "bm25_results": bm25_results,
        }

    # ==============================================================
    # Identifier Detection
    # ==============================================================

    @staticmethod
    def _extract_identifier(
        query: str,
    ) -> Optional[str]:

        match = re.search(
            r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            query,
        )

        if match:
            return match.group(1)

        match = re.search(
            r"`([A-Za-z_][A-Za-z0-9_]*)`",
            query,
        )

        if match:
            return match.group(1)

        return None

    # ==============================================================
    # Exact Identifier Search
    # ==============================================================

    @staticmethod
    def _find_exact_identifier(
        results: List,
        identifier: str,
    ) -> Optional[Dict]:

        identifier_lower = identifier.lower()

        for result in results:

            if hasattr(result, "metadata"):

                metadata = result.metadata

                name = metadata.get(
                    "name",
                    "",
                )

                qualified_name = metadata.get(
                    "qualified_name",
                    "",
                )

                chunk = {
                    "chunk_id": metadata.get(
                        "chunk_id"
                    ),
                    "code": result.page_content,
                    **metadata,
                }

            else:

                chunk = result

                name = chunk.get(
                    "name",
                    "",
                )

                qualified_name = chunk.get(
                    "qualified_name",
                    "",
                )

            if (
                str(name).lower()
                == identifier_lower
            ):

                return chunk

            if (
                str(qualified_name).lower()
                == identifier_lower
            ):

                return chunk

        return None

    # ==============================================================
    # Mark Exact Matches
    # ==============================================================

    @staticmethod
    def _mark_exact_matches(
        results: List,
        identifier: str,
    ) -> List:

        identifier_lower = identifier.lower()

        updated = []

        for result in results:

            if hasattr(result, "metadata"):

                metadata = result.metadata

                name = metadata.get(
                    "name",
                    "",
                )

                qualified_name = metadata.get(
                    "qualified_name",
                    "",
                )

                if (
                    str(name).lower()
                    == identifier_lower
                    or
                    str(qualified_name).lower()
                    == identifier_lower
                ):

                    metadata[
                        "is_exact_identifier_match"
                    ] = True

                updated.append(result)

            else:

                result = result.copy()

                name = result.get(
                    "name",
                    "",
                )

                qualified_name = result.get(
                    "qualified_name",
                    "",
                )

                if (
                    str(name).lower()
                    == identifier_lower
                    or
                    str(qualified_name).lower()
                    == identifier_lower
                ):

                    result[
                        "is_exact_identifier_match"
                    ] = True

                updated.append(result)

        return updated

    # ==============================================================
    # Helpers
    # ==============================================================

    @staticmethod
    def _get_chunk_id(
        result,
    ):

        if hasattr(result, "metadata"):

            return result.metadata.get(
                "chunk_id"
            )

        return result.get(
            "chunk_id"
        )

    @staticmethod
    def _debug_result(
        result,
    ) -> Dict:

        if hasattr(result, "metadata"):

            return {
                "chunk_id": result.metadata.get(
                    "chunk_id"
                ),
                "name": result.metadata.get(
                    "name"
                ),
                "qualified_name": result.metadata.get(
                    "qualified_name"
                ),
                "file_path": result.metadata.get(
                    "file_path"
                ),
                "type": result.metadata.get(
                    "type"
                ),
            }

        return {
            "chunk_id": result.get(
                "chunk_id"
            ),
            "name": result.get(
                "name"
            ),
            "qualified_name": result.get(
                "qualified_name"
            ),
            "file_path": result.get(
                "file_path"
            ),
            "type": result.get(
                "type"
            ),
        }