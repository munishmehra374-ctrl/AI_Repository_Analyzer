from __future__ import annotations

import logging
from typing import Dict, List

from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class ReciprocalRankFusion:
    """
    Reciprocal Rank Fusion (RRF).

    Combines Vector Search and BM25 rankings.
    """

    def __init__(self, k: int = 60) -> None:
        if k <= 0:
            raise ValueError("RRF parameter 'k' must be greater than zero.")

        self._k = k

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def fuse(
        self,
        vector_results: List,
        bm25_results: List,
    ) -> List[Dict]:

        logger.info(
            "Running Reciprocal Rank Fusion (Vector=%d BM25=%d)",
            len(vector_results),
            len(bm25_results),
        )

        fused_scores: Dict[str, Dict] = {}

        self._accumulate_scores(fused_scores, vector_results)
        self._accumulate_scores(fused_scores, bm25_results)

        fused_results = []

        for value in fused_scores.values():
            chunk = value["chunk"].copy()
            chunk["rrf_score"] = value["score"]
            fused_results.append(chunk)

        fused_results.sort(
            key=lambda x: x["rrf_score"],
            reverse=True,
        )

        return fused_results

    # ------------------------------------------------------------------ #
    # Internal Helpers
    # ------------------------------------------------------------------ #

    def _accumulate_scores(
        self,
        fused_scores: Dict[str, Dict],
        ranked_results: List,
    ) -> None:

        for rank, chunk in enumerate(ranked_results, start=1):

            # -------- LangChain Document --------
            if isinstance(chunk, Document):
                chunk_dict = {
                    "chunk_id": chunk.metadata.get("chunk_id"),
                    "code": chunk.page_content,
                    **chunk.metadata,
                }

            # -------- Dictionary --------
            else:
                chunk_dict = chunk

            chunk_id = chunk_dict.get("chunk_id")

            if chunk_id is None:
                raise KeyError(
                    "Every retrieved chunk must contain 'chunk_id'."
                )

            if chunk_id not in fused_scores:
                fused_scores[chunk_id] = {
                    "score": 0.0,
                    "chunk": chunk_dict,
                }

            fused_scores[chunk_id]["score"] += (
                1.0 / (self._k + rank)
            )