from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.retrieval.bm25_index import BM25Index

logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    BM25 keyword-based retriever.
    """

    def __init__(self, bm25_index: BM25Index):
        self._bm25_index = bm25_index

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: Optional[float] = None,
    ) -> List[Dict]:

        if not self._bm25_index.is_ready():
            raise RuntimeError("BM25 index has not been built.")

        if not query.strip():
            logger.warning("Empty query received.")
            return []

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_tokens = self._tokenize(query)

        bm25 = self._bm25_index.get_index()
        chunks = self._bm25_index.get_chunks()

        print("\n========== BM25 INDEX ==========")
        print(f"Total indexed chunks: {len(chunks)}")
        print("First chunk:")
        print(chunks[0])

        scores = bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(scores)),
            key=scores.__getitem__,
            reverse=True,
        )

        results: List[Dict] = []

        for idx in ranked_indices:

            score = float(scores[idx])

            if min_score is not None and score < min_score:
                continue

            original_chunk = chunks[idx]

            print("\n========== ORIGINAL BM25 CHUNK ==========")
            print(original_chunk)

            chunk = original_chunk.copy()

            chunk["bm25_score"] = score

            print("\n========== CHUNK BEFORE APPEND ==========")
            print(chunk)

            if "chunk_id" not in chunk:
                print("\n********** BM25 ERROR **********")
                print("chunk_id is missing!")
                print("Keys:", list(chunk.keys()))
                print(chunk)
                print("*******************************")

            results.append(chunk)

            if len(results) >= top_k:
                break

        print("\n========== BM25 FINAL RESULT ==========")
        if results:
            print(results[0])

        logger.info(
            "BM25 retrieved %d chunks for query='%s'",
            len(results),
            query,
        )

        return results

    def _tokenize(self, text: str) -> List[str]:
        return BM25Index._tokenize(text)