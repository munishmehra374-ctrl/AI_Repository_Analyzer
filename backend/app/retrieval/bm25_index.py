from __future__ import annotations

import logging
import pickle
import re
import shutil

from pathlib import Path
from typing import Dict, List, Optional

from rank_bm25 import BM25Okapi


logger = logging.getLogger(__name__)


class BM25Index:
    """
    Repository-isolated BM25 index.

    Each repository has its own persisted index:

        bm25_db/
            <repository_id>/
                bm25.pkl
                chunks.pkl
    """

    TOKEN_PATTERN = re.compile(
        r"[A-Za-z_][A-Za-z0-9_]*"
        r"|\d+"
        r"|==|!=|<=|>="
        r"|[-+*/%=(){}\[\].,:;]"
    )

    def __init__(self) -> None:

        self._bm25: Optional[BM25Okapi] = None
        self._chunks: List[Dict] = []
        self._tokenized_chunks: List[List[str]] = []
        self._repository_id: str | None = None

    # ==============================================================
    # Build
    # ==============================================================

    def build_index(
        self,
        chunks: List[Dict],
        repository_id: str,
    ) -> None:

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        if not chunks:
            raise ValueError(
                "Cannot build BM25 index from an empty chunk list."
            )

        self._validate_chunks(chunks)

        # Make sure every chunk belongs to this repository.
        repository_chunks = []

        for chunk in chunks:

            chunk_copy = chunk.copy()

            chunk_copy["repository_id"] = repository_id

            repository_chunks.append(
                chunk_copy
            )

        self._repository_id = repository_id
        self._chunks = repository_chunks

        print(
            "\n========== BM25 INDEXED CHUNKS =========="
        )

        print(
            "Repository:",
            repository_id,
        )

        for chunk in self._chunks:

            print(
                chunk.get("name"),
                "|",
                chunk.get("type"),
                "|",
                chunk.get("file_path"),
            )

        print(
            "=========================================\n"
        )

        # ==========================================================
        # Build Retrieval Text
        # ==========================================================

        retrieval_documents = [
            self._build_retrieval_text(chunk)
            for chunk in self._chunks
        ]

        self._tokenized_chunks = [
            self._tokenize(text)
            for text in retrieval_documents
        ]

        self._bm25 = BM25Okapi(
            self._tokenized_chunks
        )

        logger.info(
            "BM25 index built successfully: repository=%s chunks=%d",
            repository_id,
            len(self._chunks),
        )

    def update_files(
    self,
    chunks: List[Dict],
    repository_id: str,
    changed_files: list[str],
) -> None:

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        if not changed_files:
            print(
                "No changed files. BM25 index unchanged."
            )
            return

        changed_files = {
            str(file_path)
            for file_path in changed_files
        }

        # ----------------------------------------------------------
        # Keep chunks belonging to unchanged files
        # ----------------------------------------------------------

        existing_chunks = []

        if (
            self._repository_id == repository_id
            and self._chunks
        ):

            existing_chunks = [
                chunk
                for chunk in self._chunks
                if str(
                    chunk.get("file_path", "")
                ) not in changed_files
            ]

        # ----------------------------------------------------------
        # Add newly generated chunks for changed files
        # ----------------------------------------------------------

        new_chunks = []

        for chunk in chunks:

            chunk_copy = chunk.copy()

            chunk_copy["repository_id"] = (
                repository_id
            )

            if str(
                chunk_copy.get("file_path", "")
            ) in changed_files:

                new_chunks.append(
                    chunk_copy
                )

        combined_chunks = (
            existing_chunks
            + new_chunks
        )

        if not combined_chunks:
            raise ValueError(
                "Cannot update BM25 index: "
                "no chunks available."
            )

        # ----------------------------------------------------------
        # Rebuild BM25 using unchanged + changed chunks
        # ----------------------------------------------------------

        self._repository_id = repository_id
        self._chunks = combined_chunks

        retrieval_documents = [
            self._build_retrieval_text(chunk)
            for chunk in self._chunks
        ]

        self._tokenized_chunks = [
            self._tokenize(text)
            for text in retrieval_documents
        ]

        self._bm25 = BM25Okapi(
            self._tokenized_chunks
        )

        print(
            "\n========== BM25 INCREMENTAL UPDATE =========="
        )

        print(
            "Repository:",
            repository_id,
        )

        print(
            "Changed files:",
            len(changed_files),
        )

        print(
            "Kept chunks:",
            len(existing_chunks),
        )

        print(
            "New chunks:",
            len(new_chunks),
        )

        print(
            "Total chunks:",
            len(self._chunks),
        )

        print(
            "==============================================\n"
        )

    # ==============================================================
    # Retrieval Text
    # ==============================================================

    @staticmethod
    def _build_retrieval_text(
        chunk: Dict,
    ) -> str:

        parts: List[str] = []

        for field in (
            "name",
            "qualified_name",
            "class_name",
            "type",
            "file_path",
        ):

            value = chunk.get(
                field,
                "",
            )

            if value:
                parts.append(
                    str(value)
                )

        for field in (
            "decorators",
            "calls",
            "dependencies",
            "base_classes",
            "parameters",
            "returns",
        ):

            value = chunk.get(
                field
            )

            if value:

                if isinstance(
                    value,
                    (list, tuple, set),
                ):

                    parts.extend(
                        str(item)
                        for item in value
                    )

                else:

                    parts.append(
                        str(value)
                    )

        code = chunk.get(
            "code",
            "",
        )

        if code:
            parts.append(
                str(code)
            )

        return " ".join(parts)

    # ==============================================================
    # Persistence
    # ==============================================================

    def save(
        self,
        directory: str | Path,
        repository_id: str | None = None,
    ) -> None:

        repository_id = (
            repository_id
            or self._repository_id
        )

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        if not self.is_ready():
            raise RuntimeError(
                "BM25 index has not been built."
            )

        directory = Path(
            directory
        )

        repository_directory = (
            directory / repository_id
        )

        repository_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(
            repository_directory / "bm25.pkl",
            "wb",
        ) as f:

            pickle.dump(
                self._bm25,
                f,
            )

        with open(
            repository_directory / "chunks.pkl",
            "wb",
        ) as f:

            pickle.dump(
                self._chunks,
                f,
            )

        logger.info(
            "BM25 index saved: repository=%s path=%s",
            repository_id,
            repository_directory,
        )

    # ==============================================================
    # Load
    # ==============================================================

    def load(
        self,
        directory: str | Path,
        repository_id: str,
    ) -> None:

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        directory = Path(
            directory
        )

        repository_directory = (
            directory / repository_id
        )

        bm25_path = (
            repository_directory / "bm25.pkl"
        )

        chunks_path = (
            repository_directory / "chunks.pkl"
        )

        if not bm25_path.exists():
            raise FileNotFoundError(
                f"BM25 index not found for repository "
                f"{repository_id}: {bm25_path}"
            )

        if not chunks_path.exists():
            raise FileNotFoundError(
                f"BM25 chunks not found for repository "
                f"{repository_id}: {chunks_path}"
            )

        with open(
            bm25_path,
            "rb",
        ) as f:

            self._bm25 = pickle.load(
                f
            )

        with open(
            chunks_path,
            "rb",
        ) as f:

            self._chunks = pickle.load(
                f
            )

        self._repository_id = (
            repository_id
        )

        # Reconstruct tokenized representation.
        retrieval_documents = [
            self._build_retrieval_text(chunk)
            for chunk in self._chunks
        ]

        self._tokenized_chunks = [
            self._tokenize(text)
            for text in retrieval_documents
        ]

        logger.info(
            "Loaded BM25 index: repository=%s chunks=%d",
            repository_id,
            len(self._chunks),
        )

    # ==============================================================
    # Clear ONE Repository
    # ==============================================================

    def clear_repository(
        self,
        directory: str | Path,
        repository_id: str,
    ) -> None:

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        directory = Path(
            directory
        )

        repository_directory = (
            directory / repository_id
        )

        if repository_directory.exists():

            shutil.rmtree(
                repository_directory
            )

            logger.info(
                "Removed BM25 index for repository=%s",
                repository_id,
            )

        if self._repository_id == repository_id:

            self.clear()

    # ==============================================================
    # Clear Current In-Memory Index
    # ==============================================================

    def clear(
        self,
    ) -> None:

        self._bm25 = None

        self._chunks.clear()

        self._tokenized_chunks.clear()

        self._repository_id = None

        logger.info(
            "BM25 index cleared."
        )

    # ==============================================================
    # State
    # ==============================================================

    def is_ready(
        self,
    ) -> bool:

        return self._bm25 is not None

    # ==============================================================
    # Accessors
    # ==============================================================

    def get_index(
        self,
    ) -> BM25Okapi:

        if self._bm25 is None:

            raise RuntimeError(
                "BM25 index is not initialized."
            )

        return self._bm25

    def get_chunks(
        self,
    ) -> List[Dict]:

        return self._chunks

    def get_repository_id(
        self,
    ) -> str | None:

        return self._repository_id

    def size(
        self,
    ) -> int:

        return len(
            self._chunks
        )

    # ==============================================================
    # Tokenizer
    # ==============================================================

    @classmethod
    def _tokenize(
        cls,
        text: str,
    ) -> List[str]:

        return cls.TOKEN_PATTERN.findall(
            text.lower()
        )

    # ==============================================================
    # Validation
    # ==============================================================

    @staticmethod
    def _validate_chunks(
        chunks: List[Dict],
    ) -> None:

        for index, chunk in enumerate(
            chunks
        ):

            if "code" not in chunk:

                raise KeyError(
                    f'Chunk {index} is missing required field "code".'
                )

            if not isinstance(
                chunk["code"],
                str,
            ):

                raise TypeError(
                    f'Chunk {index} field "code" must be a string.'
                )