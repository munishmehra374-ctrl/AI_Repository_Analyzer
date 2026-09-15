from __future__ import annotations

import logging
from typing import Callable, Dict, List


logger = logging.getLogger(__name__)


class ContextOptimizer:
    """
    Optimizes retrieved chunks before sending them to the LLM.

    Responsibilities
    ----------------
    - Remove duplicate chunks.
    - Keep the highest scoring duplicate.
    - Remove invalid chunks.
    - Sort by retrieval relevance.
    - Prioritize exact identifier matches.
    - Select chunks within a token budget.

    Token counting and budget configuration are injected so this
    class remains independent of any LLM provider.
    """

    def __init__(
        self,
        max_chunks: int,
        context_token_budget: int,
        token_counter: Callable[[str], int],
    ) -> None:

        if max_chunks <= 0:
            raise ValueError(
                "max_chunks must be greater than zero."
            )

        if context_token_budget <= 0:
            raise ValueError(
                "context_token_budget must be greater than zero."
            )

        if not callable(token_counter):
            raise TypeError(
                "token_counter must be callable."
            )

        self._max_chunks = max_chunks
        self._context_token_budget = context_token_budget
        self._token_counter = token_counter

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def optimize(
        self,
        chunks: List[Dict],
    ) -> List[Dict]:

        if not chunks:
            logger.info(
                "No chunks to optimize."
            )
            return []

        print(
            "\n========== OPTIMIZER INPUT =========="
        )

        print(
            "TYPE:",
            type(chunks),
        )

        print(
            "COUNT:",
            len(chunks),
        )

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
        # Sort by relevance
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

            if self._is_valid(chunk):
                valid_chunks.append(chunk)

        optimized_chunks = valid_chunks

        print(
            "AFTER VALIDATION:",
            len(optimized_chunks),
        )

        # --------------------------------------------------------------
        # Token-aware selection
        # --------------------------------------------------------------

        final_chunks: List[Dict] = []

        used_tokens = 0

        exact_chunks = [
            chunk
            for chunk in optimized_chunks
            if chunk.get(
                "is_exact_identifier_match",
                False,
            )
        ]

        normal_chunks = [
            chunk
            for chunk in optimized_chunks
            if not chunk.get(
                "is_exact_identifier_match",
                False,
            )
        ]

        candidates = exact_chunks + normal_chunks

        for chunk in candidates:

            if len(final_chunks) >= self._max_chunks:
                break

            code = chunk.get(
                "code",
                "",
            )

            if not code:
                continue

            chunk_tokens = self._token_count(
                code
            )

            # ----------------------------------------------------------
            # Skip chunks that do not fit.
            #
            # We do NOT truncate code because retrieved repository
            # code must remain intact.
            # ----------------------------------------------------------

            if (
                used_tokens + chunk_tokens
                > self._context_token_budget
            ):

                logger.debug(
                    "Skipping chunk %s: token budget exceeded.",
                    chunk.get("chunk_id"),
                )

                continue

            final_chunks.append(chunk)

            used_tokens += chunk_tokens

        # --------------------------------------------------------------
        # Diagnostics
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
            "Context token budget:",
            self._context_token_budget,
        )

        print(
            "Context tokens used:",
            used_tokens,
        )

        print(
            "Remaining tokens:",
            self._context_token_budget - used_tokens,
        )

        if final_chunks:

            print(
                "\nSelected chunks:"
            )

            for index, chunk in enumerate(
                final_chunks,
                start=1,
            ):

                print(
                    f"{index}.",
                    chunk.get("name"),
                    "|",
                    chunk.get("file_path"),
                    "| tokens:",
                    self._token_count(
                        chunk.get("code", "")
                    ),
                    "| exact:",
                    chunk.get(
                        "is_exact_identifier_match",
                        False,
                    ),
                )

        print(
            "=======================================\n"
        )

        return final_chunks

    # ------------------------------------------------------------------
    # Token Counting
    # ------------------------------------------------------------------

    def _token_count(
        self,
        text: str,
    ) -> int:

        if not text:
            return 0

        return self._token_counter(text)

    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    @staticmethod
    def _score(
        chunk: Dict,
    ) -> float:

        return max(
            chunk.get(
                "cross_encoder_score",
                0.0,
            ),
            chunk.get(
                "rrf_score",
                0.0,
            ),
            chunk.get(
                "bm25_score",
                0.0,
            ),
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    @staticmethod
    def _is_valid(
        chunk: Dict,
    ) -> bool:

        return (
            isinstance(
                chunk,
                dict,
            )
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

    # ------------------------------------------------------------------
    # Deduplication
    # ------------------------------------------------------------------

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