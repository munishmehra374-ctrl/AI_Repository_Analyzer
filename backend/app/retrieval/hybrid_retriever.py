from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List

from app.retrieval.bm25_retriever import BM25Retriever
from app.vectorstore.retriever import RepositoryRetriever

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Executes both Vector Search and BM25 Search.

    Responsibilities
    ----------------
    - Execute both retrieval systems.
    - Return their independent results.

    This class DOES NOT:
    - Merge results.
    - Perform Reciprocal Rank Fusion.
    - Re-rank results.
    """

    def __init__(
        self,
        vector_retriever: RepositoryRetriever,
        bm25_retriever: BM25Retriever,
    ) -> None:

        self._vector_retriever = vector_retriever
        self._bm25_retriever = bm25_retriever

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def retrieve(
        self,
        query: str,
        vector_k: int = 10,
        bm25_k: int = 10,
    ) -> Dict[str, List]:
        """
        Execute vector search and BM25 retrieval in parallel.

        Parameters
        ----------
        query:
            User query.

        vector_k:
            Number of vector search results.

        bm25_k:
            Number of BM25 search results.

        Returns
        -------
        dict
            {
                "vector_results": [...],
                "bm25_results": [...]
            }
        """

        if not query.strip():
            logger.warning("Empty query received.")
            return {
                "vector_results": [],
                "bm25_results": [],
            }

        if vector_k <= 0:
            raise ValueError("vector_k must be greater than zero.")

        if bm25_k <= 0:
            raise ValueError("bm25_k must be greater than zero.")

        logger.info("Running hybrid retrieval.")

        with ThreadPoolExecutor(max_workers=2) as executor:

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

            print("\n===== HYBRID BM25 RESULT =====")
            print(bm25_results[0])

        logger.info(
            "Hybrid retrieval completed. "
            "Vector=%d BM25=%d",
            len(vector_results),
            len(bm25_results),
        )

        return {
            "vector_results": vector_results,
            "bm25_results": bm25_results,
        }