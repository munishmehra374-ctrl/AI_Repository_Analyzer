from __future__ import annotations

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ContextOptimizer:
    """
    Optimizes retrieved chunks before sending them to the LLM.

    Responsibilities
    ----------------
    - Remove duplicate chunks.
    - Keep the highest scoring duplicate.
    - Remove invalid chunks.
    - Sort by retrieval score.
    - Limit the number of chunks.

    This class DOES NOT:
    - Retrieve documents.
    - Re-rank documents.
    - Generate LLM prompts.
    """

    def __init__(self, max_chunks: int = 10) -> None:

        if max_chunks <= 0:
            raise ValueError("max_chunks must be greater than zero.")

        self._max_chunks = max_chunks

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def optimize(
        self,
        chunks: List[Dict],
    ) -> List[Dict]:
        """
        Optimize retrieved chunks before passing them to the LLM.
        """

        if not chunks:
            logger.info("No chunks to optimize.")
            return []

        unique_chunks = self._remove_duplicates(chunks)

        optimized_chunks = sorted(
            unique_chunks.values(),
            key=self._score,
            reverse=True,
        )

        optimized_chunks = [
            chunk
            for chunk in optimized_chunks
            if self._is_valid(chunk)
        ]

        logger.info(
            "Context optimized: %d -> %d chunks",
            len(chunks),
            len(optimized_chunks),
        )

        return optimized_chunks[: self._max_chunks]

    # ------------------------------------------------------------------ #
    # Internal Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _score(chunk: Dict) -> float:
        """
        Preferred ranking score.

        Priority

        1. Cross Encoder
        2. RRF
        3. BM25
        """

        return (
            chunk.get("cross_encoder_score")
            or chunk.get("rrf_score")
            or chunk.get("bm25_score")
            or 0.0
        )

    @staticmethod
    def _is_valid(chunk: Dict) -> bool:
        """
        Basic validation.
        """

        return (
            "chunk_id" in chunk
            and "code" in chunk
            and bool(chunk["code"].strip())
        )

    def _remove_duplicates(
        self,
        chunks: List[Dict],
    ) -> Dict[str, Dict]:
        """
        Keep only the highest-scoring chunk for each chunk_id.
        """

        unique_chunks: Dict[str, Dict] = {}

        for chunk in chunks:

            chunk_id = chunk["chunk_id"]

            if chunk_id not in unique_chunks:

                unique_chunks[chunk_id] = chunk
                continue

            if self._score(chunk) > self._score(unique_chunks[chunk_id]):

                unique_chunks[chunk_id] = chunk

        return unique_chunks