from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from app.retrieval.bm25_retriever import BM25Retriever
from app.vectorstore.retriever import RepositoryRetriever


logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Executes Vector Search and BM25 Search.

    Existing retrieval logic is preserved.
    Repository ID is only used to isolate retrieval
    to the selected repository.
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
        vector_k: int = 20,
        bm25_k: int = 20,
        entity_name: str | None = None,
        repository_id: str | None = None,
    ) -> Dict[str, List]:

        if not query or not query.strip():

            logger.warning(
                "Empty query received."
            )

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

        if not repository_id:

            raise ValueError(
                "repository_id is required for hybrid retrieval."
            )

        print(
            "\n========== HYBRID RETRIEVAL =========="
        )

        print(
            "Query:",
            query,
        )

        print(
            "Repository:",
            repository_id,
        )

        print(
            "Resolved Entity:",
            entity_name,
        )

        # ----------------------------------------------------------
        # Run Vector Search and BM25 Search concurrently
        # ----------------------------------------------------------

        with ThreadPoolExecutor(
            max_workers=2
        ) as executor:

            vector_future = executor.submit(
                self._vector_retriever.retrieve,
                query=query,
                top_k=vector_k,
                repository_id=repository_id,
            )

            bm25_future = executor.submit(
                self._bm25_retriever.retrieve,
                query=query,
                top_k=bm25_k,
                repository_id=repository_id,
            )

            vector_results = (
                vector_future.result()
            )

            bm25_results = (
                bm25_future.result()
            )

            if entity_name:

                exact_entity = (
                    self._bm25_retriever.retrieve_exact_entity(
                        entity_name,
                        repository_id=repository_id,
                    )
                )

                if exact_entity is not None:

                    existing_ids = {
                        result.get("chunk_id")
                        for result in bm25_results
                    }

                    exact_id = exact_entity.get(
                        "chunk_id"
                    )

                    if exact_id not in existing_ids:

                        bm25_results.insert(
                            0,
                            exact_entity
                        )

        # ----------------------------------------------------------
        # Entity-aware prioritization
        # ----------------------------------------------------------

        if entity_name:

            vector_results = (
                self._prioritize_entity(
                    vector_results,
                    entity_name,
                )
            )

            bm25_results = (
                self._prioritize_entity(
                    bm25_results,
                    entity_name,
                )
            )

        # ----------------------------------------------------------
        # Debug
        # ----------------------------------------------------------

        print(
            "\nVector Results:",
            len(vector_results),
        )

        print(
            "BM25 Results:",
            len(bm25_results),
        )

        if entity_name:

            exact_vector = (
                self._find_exact_entity(
                    vector_results,
                    entity_name,
                )
            )

            exact_bm25 = (
                self._find_exact_entity(
                    bm25_results,
                    entity_name,
                )
            )

            print(
                "\n========== ENTITY PRIORITIZATION =========="
            )

            print(
                "Entity:",
                entity_name,
            )

            print(
                "Found in Vector:",
                exact_vector is not None,
            )

            print(
                "Found in BM25:",
                exact_bm25 is not None,
            )

            print(
                "============================================\n"
            )

        print(
            "\n=====================================\n"
        )

        return {
            "vector_results": vector_results,
            "bm25_results": bm25_results,
        }

    # ==============================================================
    # Entity Helpers
    # ==============================================================

    @staticmethod
    def _get_metadata_value(
        result,
        key: str,
        default="",
    ):

        if hasattr(
            result,
            "metadata",
        ):

            return result.metadata.get(
                key,
                default,
            )

        if isinstance(
            result,
            dict,
        ):

            return result.get(
                key,
                default,
            )

        return default

    @classmethod
    def _find_exact_entity(
        cls,
        results: List,
        entity_name: str,
    ):

        target = (
            entity_name
            .strip()
            .lower()
        )

        for result in results:

            name = str(
                cls._get_metadata_value(
                    result,
                    "name",
                    "",
                )
            ).strip().lower()

            qualified_name = str(
                cls._get_metadata_value(
                    result,
                    "qualified_name",
                    "",
                )
            ).strip().lower()

            if (
                name == target
                or qualified_name == target
            ):

                return result

        return None

    @classmethod
    def _prioritize_entity(
        cls,
        results: List,
        entity_name: str,
    ) -> List:

        if not results or not entity_name:

            return results

        target = (
            entity_name
            .strip()
            .lower()
        )

        exact_matches = []
        remaining = []

        for result in results:

            name = str(
                cls._get_metadata_value(
                    result,
                    "name",
                    "",
                )
            ).strip().lower()

            qualified_name = str(
                cls._get_metadata_value(
                    result,
                    "qualified_name",
                    "",
                )
            ).strip().lower()

            if (
                name == target
                or qualified_name == target
            ):

                exact_matches.append(
                    result
                )

            else:

                remaining.append(
                    result
                )

        return (
            exact_matches
            + remaining
        )