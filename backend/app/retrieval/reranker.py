from __future__ import annotations

import logging
from typing import Dict, List, Optional

from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """
    Re-ranks retrieved chunks using a Cross Encoder model.

    Responsibilities
    ----------------
    - Score (query, chunk) pairs.
    - Sort chunks by relevance.
    - Return the top-k results.

    This class DOES NOT:
    - Retrieve documents.
    - Merge retrieval results.
    - Optimize context.
    """

    DEFAULT_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
    ) -> None:

        logger.info("Loading Cross Encoder model: %s", model_name)

        self._model = CrossEncoder(model_name)

        logger.info("Cross Encoder loaded successfully.")

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def rerank(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = 10,
    ) -> List[Dict]:
        """
        Re-rank retrieved chunks.

        Parameters
        ----------
        query:
            User query.

        chunks:
            Retrieved chunks.

        top_k:
            Number of chunks to return.

        Returns
        -------
        List[Dict]
            Re-ranked chunks sorted by Cross Encoder score.
        """

        if not query.strip():
            logger.warning("Empty query received.")
            return []

        if not chunks:
            logger.info("No chunks to rerank.")
            return []

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        self._validate_chunks(chunks)

        sentence_pairs = [
            (query, chunk["code"])
            for chunk in chunks
        ]

        scores = self._model.predict(sentence_pairs)

        reranked_chunks: List[Dict] = []

        for chunk, score in zip(chunks, scores):

            item = chunk.copy()

            item["cross_encoder_score"] = float(score)

            reranked_chunks.append(item)

        reranked_chunks.sort(
            key=lambda chunk: chunk["cross_encoder_score"],
            reverse=True,
        )

        logger.info(
            "Cross Encoder reranked %d chunks.",
            len(reranked_chunks),
        )

        return reranked_chunks[:top_k]

    # ------------------------------------------------------------------ #
    # Internal Helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _validate_chunks(chunks: List[Dict]) -> None:
        """
        Validate chunk schema.
        """

        for index, chunk in enumerate(chunks):

            if "code" not in chunk:
                raise KeyError(
                    f'Chunk {index} is missing required field "code".'
                )

            if not isinstance(chunk["code"], str):
                raise TypeError(
                    f'Chunk {index} field "code" must be a string.'
                )