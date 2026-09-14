from __future__ import annotations

import logging
from typing import Dict, List, Optional

from app.retrieval.bm25_index import BM25Index

import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")


logger = logging.getLogger(__name__)


class BM25Retriever:
    """
    BM25 keyword-based retriever.
    """

    MAX_CHUNKS_PER_FILE = 3

    def __init__(
        self,
        bm25_index: BM25Index,
    ):
        self._bm25_index = bm25_index

    # ==============================================================
    # BM25 Retrieval
    # ==============================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        min_score: Optional[float] = None,
        repository_id: str | None = None,
    ) -> List[Dict]:

        if not self._bm25_index.is_ready():
            raise RuntimeError(
                "BM25 index has not been built."
            )

        if not query.strip():
            logger.warning(
                "Empty query received."
            )
            return []

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        # ----------------------------------------------------------
        # Repository isolation
        # ----------------------------------------------------------

        if repository_id is not None:

            indexed_repository_id = (
                self._bm25_index.get_repository_id()
            )

            if indexed_repository_id != repository_id:

                raise ValueError(
                    "BM25 index does not belong to "
                    f"repository '{repository_id}'. "
                    f"Loaded repository: "
                    f"'{indexed_repository_id}'."
                )

        query_tokens = self._tokenize(
            query
        )

        bm25 = self._bm25_index.get_index()
        chunks = self._bm25_index.get_chunks()

        # ==========================================================
        # BM25 Scoring
        # ==========================================================

        scores = bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=scores.__getitem__,
            reverse=True,
        )

        results: List[Dict] = []

        # Keep one file from dominating the results.
        file_counts: Dict[str, int] = {}

        # ==========================================================
        # Build Diverse Results
        # ==========================================================

        for idx in ranked_indices:

            score = float(
                scores[idx]
            )

            if (
                min_score is not None
                and score < min_score
            ):
                continue

            original_chunk = chunks[idx]

            # ------------------------------------------------------
            # Extra safety check
            # ------------------------------------------------------

            if (
                repository_id is not None
                and original_chunk.get(
                    "repository_id"
                ) != repository_id
            ):
                continue

            chunk = original_chunk.copy()

            chunk["bm25_score"] = score

            file_path = str(
                chunk.get(
                    "file_path",
                    "",
                )
            )

            if not file_path:
                file_path = (
                    f"__unknown_file_{idx}"
                )

            current_count = file_counts.get(
                file_path,
                0,
            )

            if (
                current_count
                >= self.MAX_CHUNKS_PER_FILE
            ):
                continue

            results.append(
                chunk
            )

            file_counts[file_path] = (
                current_count + 1
            )

            if len(results) >= top_k:
                break

        # ==========================================================
        # Debug
        # ==========================================================

        print(
            "\n========== BM25 FINAL RESULT =========="
        )

        print(
            "Requested:",
            top_k,
        )

        print(
            "Selected:",
            len(results),
        )

        print(
            "\n----- Selected Files -----"
        )

        for index, chunk in enumerate(
            results
        ):

            print(
                f"{index}:",
                chunk.get("name"),
                "|",
                chunk.get("qualified_name"),
                "|",
                chunk.get("file_path"),
                "| Score:",
                chunk.get("bm25_score"),
            )

        print(
            "========================================\n"
        )

        logger.info(
            "BM25 retrieved %d diverse chunks for query='%s'",
            len(results),
            query,
        )

        return results

    # ==============================================================
    # Exact Entity Lookup
    # ==============================================================

    def retrieve_exact_entity(
        self,
        entity_name: str,
        repository_id: str | None = None,
    ) -> Optional[Dict]:

        if not self._bm25_index.is_ready():

            raise RuntimeError(
                "BM25 index has not been built."
            )

        if not entity_name:
            return None

        target = (
            entity_name
            .strip()
            .lower()
        )

        if not target:
            return None

        chunks = (
            self._bm25_index.get_chunks()
        )

        print(
            "\n========== EXACT ENTITY LOOKUP =========="
        )

        print(
            "Searching for:",
            entity_name,
        )

        print(
            "Indexed chunks:",
            len(chunks),
        )

        # ==========================================================
        # Search indexed chunks
        # ==========================================================

        for chunk in chunks:

            # ------------------------------------------------------
            # Repository isolation
            # ------------------------------------------------------

            if (
                repository_id is not None
                and chunk.get(
                    "repository_id"
                ) != repository_id
            ):
                continue

            name = str(
                chunk.get(
                    "name",
                    "",
                )
            ).strip().lower()

            qualified_name = str(
                chunk.get(
                    "qualified_name",
                    "",
                )
            ).strip().lower()

            # ------------------------------------------------------
            # Exact name match
            # ------------------------------------------------------

            if name == target:

                result = chunk.copy()

                result["bm25_score"] = 0.0

                result[
                    "exact_entity_match"
                ] = True

                print(
                    "\n========== EXACT ENTITY FOUND =========="
                )

                print(
                    "Entity:",
                    entity_name,
                )

                print(
                    "Name:",
                    name,
                )

                print(
                    "Qualified:",
                    qualified_name,
                )

                print(
                    "File:",
                    chunk.get(
                        "file_path"
                    ),
                )

                print(
                    "Chunk ID:",
                    chunk.get(
                        "chunk_id"
                    ),
                )

                print(
                    "========================================\n"
                )

                return result

            # ------------------------------------------------------
            # Exact qualified-name match
            # ------------------------------------------------------

            if qualified_name == target:

                result = chunk.copy()

                result["bm25_score"] = 0.0

                result[
                    "exact_entity_match"
                ] = True

                print(
                    "\n========== EXACT ENTITY FOUND =========="
                )

                print(
                    "Entity:",
                    entity_name,
                )

                print(
                    "Name:",
                    name,
                )

                print(
                    "Qualified:",
                    qualified_name,
                )

                print(
                    "File:",
                    chunk.get(
                        "file_path"
                    ),
                )

                print(
                    "Chunk ID:",
                    chunk.get(
                        "chunk_id"
                    ),
                )

                print(
                    "========================================\n"
                )

                return result

        # ==========================================================
        # Entity Not Found
        # ==========================================================

        print(
            "\n========== EXACT ENTITY NOT IN INDEX =========="
        )

        print(
            "Entity:",
            entity_name,
        )

        print(
            "===============================================\n"
        )

        return None

    # ==============================================================
    # Tokenizer
    # ==============================================================

    def _tokenize(
        self,
        text: str,
    ) -> List[str]:

        return BM25Index._tokenize(
            text
        )