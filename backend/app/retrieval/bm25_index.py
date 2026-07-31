from __future__ import annotations

import logging
import pickle
import re
from pathlib import Path
from typing import Dict, List, Optional

from rank_bm25 import BM25Okapi


logger = logging.getLogger(__name__)


class BM25Index:
    """
    BM25 index for repository code chunks.

    Responsibilities
    ----------------
    - Build BM25 index
    - Persist index to disk
    - Load index from disk
    - Provide access to indexed chunks

    This class DOES NOT perform retrieval.
    """

    TOKEN_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|[-+*/%=(){}[\].,:;]")

    def __init__(self) -> None:
        self._bm25: Optional[BM25Okapi] = None
        self._chunks: List[Dict] = []
        self._tokenized_chunks: List[List[str]] = []

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def build_index(self, chunks: List[Dict]) -> None:
        """
        Build BM25 index from repository chunks.

        Parameters
        ----------
        chunks:
            List of chunk dictionaries.
            Every chunk must contain a "code" field.
        """

        if not chunks:
            raise ValueError("Cannot build BM25 index from an empty chunk list.")

        self._validate_chunks(chunks)

        print("First BM25 chunk:")
        print(chunks[0])
        self._chunks = chunks

        self._tokenized_chunks = [
            self._tokenize(chunk["code"])
            for chunk in chunks
        ]

        self._bm25 = BM25Okapi(self._tokenized_chunks)

        logger.info(
            "BM25 index built successfully with %d chunks.",
            len(chunks),
        )

    def save(self, directory: str | Path) -> None:
        """
        Save BM25 index to disk.
        """

        if not self.is_ready():
            raise RuntimeError("BM25 index has not been built.")

        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)

        with open(directory / "bm25.pkl", "wb") as f:
            pickle.dump(self._bm25, f)

        with open(directory / "chunks.pkl", "wb") as f:
            pickle.dump(self._chunks, f)

        logger.info("BM25 index saved to %s", directory)

    def load(self, directory: str | Path) -> None:
        """
        Load BM25 index from disk.
        """

        directory = Path(directory)

        with open(directory / "bm25.pkl", "rb") as f:
            self._bm25 = pickle.load(f)

        with open(directory / "chunks.pkl", "rb") as f:
            self._chunks = pickle.load(f)

        self._tokenized_chunks = [
            self._tokenize(chunk["code"])
            for chunk in self._chunks
        ]

        logger.info(
            "Loaded BM25 index containing %d chunks.",
            len(self._chunks),
        )

    def clear(self) -> None:
        """
        Remove the current index from memory.
        """

        self._bm25 = None
        self._chunks.clear()
        self._tokenized_chunks.clear()

        logger.info("BM25 index cleared.")

    def is_ready(self) -> bool:
        """
        Returns True if the index has been built.
        """

        return self._bm25 is not None

    def get_index(self) -> BM25Okapi:
        """
        Return BM25 object.
        """

        if self._bm25 is None:
            raise RuntimeError("BM25 index is not initialized.")

        return self._bm25

    def get_chunks(self) -> List[Dict]:
        """
        Return indexed chunks.
        """

        return self._chunks

    def size(self) -> int:
        """
        Number of indexed chunks.
        """

        return len(self._chunks)

    # ------------------------------------------------------------------ #
    # Internal Helpers
    # ------------------------------------------------------------------ #

    @classmethod
    def _tokenize(cls, text: str) -> List[str]:
        """
        Tokenizer designed for source code.

        Example
        -------
        def verify_token(user_id):

        becomes

        ['def',
         'verify_token',
         '(',
         'user_id',
         ')']
        """

        return cls.TOKEN_PATTERN.findall(text.lower())

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