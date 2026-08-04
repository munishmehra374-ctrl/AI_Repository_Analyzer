from app.retrieval.bm25_index import BM25Index
from app.services.chunk_service import ChunkService
from app.services.repository_reader import RepositoryReader
from app.vectorstore.chroma_store import ChromaStore

from app.knowledge.graph_service import GraphService
from app.services.repository_metadata_service import RepositoryMetadataService


class IndexingService:

    DEBUG = False
    MAX_FILES = 3
    MAX_CHUNKS = 50

    def __init__(self):

        self.repository_reader = RepositoryReader()

        self.chunk_service = ChunkService()

        # Pipeline 1
        self.vector_store = ChromaStore()
        self.bm25_index = BM25Index()

        # Pipeline 2
        self.graph_service = GraphService()

        # Pipeline 3
        self.metadata_service = RepositoryMetadataService()

    # =====================================================
    # Repository Indexing
    # =====================================================

    def index_repository(self, repository_path: str):

        source_files = self.repository_reader.get_source_files(
            repository_path
        )

        if self.DEBUG:

            source_files = source_files[:self.MAX_FILES]

            print(
                f"[DEBUG] Processing only {len(source_files)} files"
            )

        print(f"Source files found: {len(source_files)}")

        all_chunks = []

        # =================================================
        # Process Every Source File
        # =================================================

        for file_path in source_files:

            result = self.chunk_service.generate_chunks(
                file_path
            )

            chunks = result["chunks"]

            extracted_data = result["ast"]

            if self.DEBUG:

                remaining = self.MAX_CHUNKS - len(all_chunks)

                if remaining <= 0:

                    print(
                        "[DEBUG] Maximum chunk limit reached."
                    )

                    break

                chunks = chunks[:remaining]

            print(
                f"{file_path} -> {len(chunks)} chunks"
            )

            all_chunks.extend(chunks)

            # --------------------------------------------
            # Pipeline 2 : Knowledge Graph
            # --------------------------------------------

            extracted_data["file_path"] = file_path

            extracted_data["repository_path"] = repository_path

            extracted_data["repository_name"] = repository_path.split("\\")[-1]

            extracted_data["language"] = "python"

            self.graph_service.build_graph(
                extracted_data=extracted_data
            )

            # --------------------------------------------
            # Pipeline 3 : Repository Profiler
            # --------------------------------------------

            self.metadata_service.update(

                extracted_data=extracted_data,

                file_path=file_path,

                repository_path=repository_path,

                language="python",
            )

        # =================================================
        # Pipeline 1 : Semantic Retrieval
        # =================================================

        self.vector_store.add_documents(
            all_chunks
        )

        self.bm25_index.build_index(
            all_chunks
        )

        repository_profile = (
            self.metadata_service.get_repository_profile()
        )

        print("\n" + "=" * 70)
        print("Repository Indexed Successfully")
        print("=" * 70)
        print(repository_profile)
        print("=" * 70)

        return {

            "status": "success",

            "files": len(source_files),

            "chunks": len(all_chunks),

            "repository_profile": repository_profile,
        }