from __future__ import annotations

from langchain_chroma import Chroma
from langchain_core.documents import Document

from .embeddings import EmbeddingModel


class ChromaStore:

    def __init__(self):

        self.embedding_model = EmbeddingModel()

        self.vectorstore = Chroma(
            collection_name="repository_chunks",
            embedding_function=self.embedding_model.model,
            persist_directory="chroma_db",
        )

    # ==========================================================
    # Remove ONE Repository
    # ==========================================================

    def clear_repository(
        self,
        repository_id: str,
    ):

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        result = self.vectorstore.get(
            where={
                "repository_id": repository_id
            }
        )

        ids = result.get("ids", [])

        if ids:

            self.vectorstore.delete(
                ids=ids
            )

        print(
            f"Cleared {len(ids)} Chroma documents "
            f"for repository {repository_id}."
        )

            # ==========================================================
    # Remove Documents For Specific Files
    # ==========================================================

    def clear_files(
        self,
        repository_id: str,
        file_paths: list[str],
    ):

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        if not file_paths:
            return 0

        result = self.vectorstore.get(
            where={
                "repository_id": repository_id
            }
        )

        ids = result.get("ids", [])
        metadatas = result.get("metadatas", [])

        ids_to_delete = []

        for document_id, metadata in zip(
            ids,
            metadatas,
        ):

            if metadata.get("file_path") in file_paths:

                ids_to_delete.append(
                    document_id
                )

        if ids_to_delete:

            self.vectorstore.delete(
                ids=ids_to_delete
            )

        print(
            f"Cleared {len(ids_to_delete)} Chroma documents "
            f"for {len(file_paths)} changed files."
        )

        return len(ids_to_delete)

    # ==========================================================
    # Add Repository Documents
    # ==========================================================

    def add_documents(
        self,
        chunks,
        repository_id: str,
    ):

        if not repository_id:
            raise ValueError(
                "repository_id is required."
            )

        documents = []

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk["code"],
                    metadata={
                        "repository_id": repository_id,
                        "chunk_id": chunk["chunk_id"],
                        "type": chunk["type"],
                        "name": chunk["name"],
                        "qualified_name": chunk.get(
                            "qualified_name",
                            "",
                        ),
                        "class_name": chunk.get(
                            "class_name",
                            "",
                        ),
                        "file_path": chunk["file_path"],
                        "language": chunk["language"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                    },
                    id=f"{repository_id}:{chunk['chunk_id']}",
                )
            )

        if not documents:
            return {
                "indexed_chunks": 0,
            }

        batch_size = 1000

        total_batches = (
            len(documents) + batch_size - 1
        ) // batch_size

        for batch_number, start in enumerate(
            range(
                0,
                len(documents),
                batch_size,
            ),
            start=1,
        ):

            end = start + batch_size
            batch = documents[start:end]

            print(
                f"Indexing batch "
                f"{batch_number}/{total_batches} "
                f"({len(batch)} documents)"
            )

            self.vectorstore.add_documents(
                batch,
                ids=[
                    document.id
                    for document in batch
                ],
            )

        print(
            f"Successfully indexed "
            f"{len(documents)} chunks "
            f"for repository {repository_id}."
        )

        return {
            "indexed_chunks": len(documents),
        }