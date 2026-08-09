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
    - Prioritize exact identifier matches.
    - Limit the number of chunks.
    - Limit total context size.

    This class DOES NOT:
    - Retrieve documents.
    - Re-rank documents.
    - Generate LLM prompts.
    """

    def __init__(
        self,
        max_chunks: int = 2,
        max_context_chars: int = 12000,
    ) -> None:

        if max_chunks <= 0:
            raise ValueError(
                "max_chunks must be greater than zero."
            )

        if max_context_chars <= 0:
            raise ValueError(
                "max_context_chars must be greater than zero."
            )

        self._max_chunks = max_chunks
        self._max_context_chars = max_context_chars

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize(
        self,
        chunks: List[Dict],
    ) -> List[Dict]:

        if not chunks:
            logger.info("No chunks to optimize.")
            return []

        print("\n========== OPTIMIZER INPUT ==========")
        print("TYPE:", type(chunks))
        print("COUNT:", len(chunks))

        for i, chunk in enumerate(chunks[:3]):

            print(f"\nCHUNK {i}")
            print(
                "TYPE:",
                type(chunk),
            )

            print(
                "KEYS:",
                list(chunk.keys())
                if isinstance(chunk, dict)
                else "NOT DICT",
            )

            print(
                "CHUNK ID:",
                chunk.get("chunk_id")
                if isinstance(chunk, dict)
                else None,
            )

            print(
                "HAS CODE:",
                "code" in chunk
                if isinstance(chunk, dict)
                else False,
            )

            print(
                "CODE TYPE:",
                type(chunk.get("code"))
                if isinstance(chunk, dict)
                else None,
            )

            print(
                "CODE LENGTH:",
                len(chunk.get("code", ""))
                if isinstance(chunk, dict)
                else 0,
            )

        print("=====================================\n")

        # --------------------------------------------------------------
        # Remove duplicates
        # --------------------------------------------------------------

        unique_chunks = self._remove_duplicates(
            chunks
        )

        print(
            "AFTER DEDUPLICATION:",
            len(unique_chunks),
        )

        # --------------------------------------------------------------
        # Sort
        # --------------------------------------------------------------

        optimized_chunks = sorted(
            unique_chunks.values(),
            key=lambda chunk: (
                bool(
                    chunk.get(
                        "is_exact_identifier_match",
                        False,
                    )
                ),
                self._score(chunk),
            ),
            reverse=True,
        )

        print(
            "AFTER SORT:",
            len(optimized_chunks),
        )

        # --------------------------------------------------------------
        # Validate
        # --------------------------------------------------------------

        valid_chunks = []

        for chunk in optimized_chunks:

            valid = self._is_valid(chunk)

            print(
                "VALID:",
                valid,
                "| chunk_id:",
                chunk.get("chunk_id"),
                "| code length:",
                len(
                    chunk.get(
                        "code",
                        "",
                    )
                ),
            )

            if valid:
                valid_chunks.append(chunk)

        optimized_chunks = valid_chunks

        print(
            "AFTER VALIDATION:",
            len(optimized_chunks),
        )

        # --------------------------------------------------------------
        # Limit number of chunks
        # --------------------------------------------------------------

        optimized_chunks = optimized_chunks[
            : self._max_chunks
        ]

        # --------------------------------------------------------------
        # Context character budget
        # --------------------------------------------------------------

        final_chunks: List[Dict] = []

        total_chars = 0

        for chunk in optimized_chunks:

            code = chunk.get(
                "code",
                "",
            )

            if not code:
                continue

            if (
                total_chars + len(code)
                > self._max_context_chars
            ):

                logger.info(
                    "Context character limit reached."
                )

                break

            final_chunks.append(chunk)

            total_chars += len(code)

        # --------------------------------------------------------------
        # Final diagnostics
        # --------------------------------------------------------------

        print(
            "\n========== CONTEXT OPTIMIZER =========="
        )

        print(
            "Input chunks:",
            len(chunks),
        )

        print(
            "After deduplication:",
            len(unique_chunks),
        )

        print(
            "After validation:",
            len(optimized_chunks),
        )

        print(
            "Final chunks:",
            len(final_chunks),
        )

        print(
            "Final context characters:",
            total_chars,
        )

        if final_chunks:

            print(
                "\nFINAL CHUNK:"
            )

            print(
                "Name:",
                final_chunks[0].get(
                    "name"
                ),
            )

            print(
                "File:",
                final_chunks[0].get(
                    "file_path"
                ),
            )

            print(
                "Chunk ID:",
                final_chunks[0].get(
                    "chunk_id"
                ),
            )

            print(
                "Exact Identifier Match:",
                final_chunks[0].get(
                    "is_exact_identifier_match",
                    False,
                ),
            )

        print(
            "=======================================\n"
        )

        return final_chunks

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _score(
        chunk: Dict,
    ) -> float:

        return (
            chunk.get("cross_encoder_score")
            or chunk.get("rrf_score")
            or chunk.get("bm25_score")
            or 0.0
        )

    @staticmethod
    def _is_valid(
        chunk: Dict,
    ) -> bool:

        return (
            isinstance(chunk, dict)
            and "chunk_id" in chunk
            and "code" in chunk
            and isinstance(
                chunk["code"],
                str,
            )
            and bool(
                chunk["code"].strip()
            )
        )

    def _remove_duplicates(
        self,
        chunks: List[Dict],
    ) -> Dict[str, Dict]:

        unique_chunks: Dict[str, Dict] = {}

        for chunk in chunks:

            if not isinstance(
                chunk,
                dict,
            ):
                continue

            chunk_id = chunk.get(
                "chunk_id"
            )

            if chunk_id is None:
                continue

            if chunk_id not in unique_chunks:

                unique_chunks[chunk_id] = chunk

                continue

            if self._score(chunk) > self._score(
                unique_chunks[chunk_id]
            ):

                unique_chunks[chunk_id] = chunk

        return unique_chunks