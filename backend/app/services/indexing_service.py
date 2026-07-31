from app.retrieval.bm25_index import BM25Index
from app.services.chunk_service import ChunkService
from app.services.repository_reader import RepositoryReader
from app.vectorstore.chroma_store import ChromaStore


class IndexingService:

    def __init__(self):

        self.repository_reader = RepositoryReader()
        self.chunk_service = ChunkService()

        self.vector_store = ChromaStore()
        self.bm25_index = BM25Index()

    def index_repository(self, repository_path: str):

        source_files = self.repository_reader.get_source_files(
            repository_path
        )

        print(f"Source files found: {len(source_files)}")

        all_chunks = []

        for file_path in source_files:

            chunks = self.chunk_service.generate_chunks(file_path)

            print(f"{file_path} -> {len(chunks)} chunks")

            all_chunks.extend(chunks)

        print(f"Total chunks: {len(all_chunks)}")

        # Show first chunk for debugging (optional)
        if all_chunks:
            print("\n========== INDEXING FIRST CHUNK ==========")
            print(all_chunks[0])
            print("Keys:", list(all_chunks[0].keys()))
            print("=========================================\n")

        # Index the complete repository
        self.vector_store.add_documents(all_chunks)

        self.bm25_index.build_index(all_chunks)

        return {
            "status": "success",
            "total_files": len(source_files),
            "total_chunks": len(all_chunks),
            "message": "Repository indexed successfully."
        }