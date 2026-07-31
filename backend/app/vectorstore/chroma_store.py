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

    def add_documents(self, chunks):

        documents = []

        for chunk in chunks:

            documents.append(
                Document(
                    page_content=chunk["code"],
                    metadata={
                        "chunk_id": chunk["chunk_id"],
                        "type": chunk["type"],
                        "name": chunk["name"],
                        "file_path": chunk["file_path"],
                        "language": chunk["language"],
                        "start_line": chunk["start_line"],
                        "end_line": chunk["end_line"],
                    },
                )
            )

        batch_size = 1000

        total_batches = (len(documents) + batch_size - 1) // batch_size

        for batch_number, start in enumerate(
            range(0, len(documents), batch_size),
            start=1,
        ):

            end = start + batch_size
            batch = documents[start:end]

            print(
                f"Indexing batch {batch_number}/{total_batches} "
                f"({len(batch)} documents)"
            )

            self.vectorstore.add_documents(batch)

        print(f"Successfully indexed {len(documents)} chunks.")

        return {
            "indexed_chunks": len(documents),
        }