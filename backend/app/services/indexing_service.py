from app.retrieval.bm25_index import BM25Index
from app.services.chunk_service import ChunkService
from app.services.repository_reader import RepositoryReader
from app.vectorstore.chroma_store import ChromaStore

from app.knowledge.graph_service import GraphService
from app.services.repository_metadata_service import RepositoryMetadataService
from app.core.redis import redis_client
from app.graph.dependencies import dependencies

import json


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

    def index_repository(
        self,
        repository_path: str,
        task_id=None,
    ):

        print("INDEXING SERVICE STARTED")
        print("TASK ID:", task_id)

        source_files = self.repository_reader.get_source_files(
            repository_path
        )

        print("FOUND FILES:", len(source_files))

        if task_id:

            redis_client.hset(
                task_id,
                mapping={
                    "status": "STARTED",
                    "stage": "Reading Repository",
                    "progress": 5,
                },
            )

            print("REDIS:")
            print(redis_client.hgetall(task_id))

        total_files = len(source_files)

        if self.DEBUG:

            source_files = source_files[
                : self.MAX_FILES
            ]

            total_files = len(source_files)

            print(
                f"[DEBUG] Processing only "
                f"{len(source_files)} files"
            )

        print(
            f"Source files found: {len(source_files)}"
        )

        # =====================================================
        # IMPORTANT
        # =====================================================

        all_chunks = []

        # Store AST/extracted data from EVERY file.
        # The graph will be built only after all files
        # have been processed.

        all_extracted_data = []

        try:

            # =================================================
            # Process Every Source File
            # =================================================

            if task_id:

                redis_client.hset(
                    task_id,
                    mapping={
                        "stage": "Parsing Source Files",
                        "progress": 10,
                    },
                )

                print("REDIS:")
                print(
                    redis_client.hgetall(
                        task_id
                    )
                )

            for index, file_path in enumerate(
                source_files
            ):

                result = (
                    self.chunk_service.generate_chunks(
                        file_path
                    )
                )

                chunks = result["chunks"]
                extracted_data = result["ast"]

                if self.DEBUG:

                    remaining = (
                        self.MAX_CHUNKS
                        - len(all_chunks)
                    )

                    if remaining <= 0:

                        print(
                            "[DEBUG] Maximum chunk "
                            "limit reached."
                        )

                        break

                    chunks = chunks[
                        :remaining
                    ]

                print(
                    f"{file_path} -> "
                    f"{len(chunks)} chunks"
                )

                all_chunks.extend(
                    chunks
                )

                # =============================================
                # Prepare Graph Data
                # =============================================

                extracted_data[
                    "file_path"
                ] = file_path

                extracted_data[
                    "repository_path"
                ] = repository_path

                extracted_data[
                    "repository_name"
                ] = repository_path.split(
                    "\\"
                )[-1]

                extracted_data[
                    "language"
                ] = "python"

                # =============================================
                # IMPORTANT:
                #
                # Do NOT build the graph here.
                #
                # Store this file's extracted data.
                # =============================================

                all_extracted_data.append(
                    extracted_data
                )

                # =============================================
                # Pipeline 3:
                # Repository Profiler
                # =============================================

                if task_id:

                    redis_client.hset(
                        task_id,
                        mapping={
                            "stage":
                                "Extracting Code Structure",
                        },
                    )

                self.metadata_service.update(
                    extracted_data=extracted_data,
                    file_path=file_path,
                    repository_path=repository_path,
                    language="python",
                )

                # =============================================
                # Redis Progress
                # =============================================

                if (
                    task_id
                    and total_files > 0
                ):

                    progress = (
                        10
                        + int(
                            (
                                (index + 1)
                                * 55
                            )
                            / total_files
                        )
                    )

                    redis_client.hset(
                        task_id,
                        mapping={
                            "status":
                                "STARTED",

                            "stage":
                                "Parsing Source Files",

                            "progress":
                                progress,

                            "current_file":
                                file_path,

                            "files_processed":
                                index + 1,

                            "total_files":
                                total_files,
                        },
                    )

                    print("REDIS:")

                    print(
                        redis_client.hgetall(
                            task_id
                        )
                    )

            # =================================================
            # Pipeline 2:
            # Knowledge Graph
            # =================================================

            # IMPORTANT:
            #
            # Build the graph ONLY ONCE,
            # AFTER ALL FILES HAVE BEEN EXTRACTED.
            #
            # This allows RelationshipBuilder to see
            # every function in the repository.

            if task_id:

                redis_client.hset(
                    task_id,
                    mapping={
                        "stage":
                            "Building Knowledge Graph",

                        "progress":
                            70,
                    },
                )

                print("REDIS:")

                print(
                    redis_client.hgetall(
                        task_id
                    )
                )

            print(
                "\n" + "=" * 70
            )

            print(
                "BUILDING COMPLETE REPOSITORY GRAPH"
            )

            print(
                "TOTAL EXTRACTED FILES:",
                len(all_extracted_data),
            )

            print(
                "=" * 70
            )

            graph = (
                self.graph_service.build_graph(
                    extracted_files=
                        all_extracted_data
                )
            )

            print(
                "FINAL GRAPH FILES:",
                len(graph.files),
            )

            print(
                "FINAL GRAPH FUNCTIONS:",
                len(graph.functions),
            )

            print(
                "FINAL GRAPH RELATIONSHIPS:",
                len(graph.relationships),
            )

            # =================================================
            # Pipeline 1:
            # Semantic Retrieval
            # =================================================

            if task_id:

                redis_client.hset(
                    task_id,
                    mapping={
                        "stage":
                            "Generating Semantic Embeddings",

                        "progress":
                            75,
                    },
                )

            self.vector_store.add_documents(
                all_chunks
            )

            if task_id:

                redis_client.hset(
                    task_id,
                    mapping={
                        "stage":
                            "Building BM25 Index",

                        "progress":
                            90,
                    },
                )

            self.bm25_index.build_index(
                all_chunks
            )

            self.bm25_index.save(
                "bm25_db"
            )
            # =================================================
            # Initialize Retrieval Pipeline
            # =================================================

            dependencies.initialize(
                vector_store=self.vector_store,
                bm25_index=self.bm25_index,
            )

            print("=" * 60)

            print(
                "DEPENDENCIES INITIALIZED"
            )

            print(
                dependencies.retrieval_service
            )

            print("=" * 60)

            # =================================================
            # Repository Profile
            # =================================================

            if task_id:

                redis_client.hset(
                    task_id,
                    mapping={
                        "stage":
                            "Generating Repository Profile",

                        "progress":
                            95,
                    },
                )

                print("REDIS:")

                print(
                    redis_client.hgetall(
                        task_id
                    )
                )

            repository_profile = (
                self.metadata_service
                .get_repository_profile()
            )

            # =================================================
            # Save Repository Profile
            # =================================================

            if task_id:

                profile_data = {
                    **repository_profile,
                    "source_files": source_files,
                }

                redis_client.set(
                    f"profile:{task_id}",
                    json.dumps(profile_data),
                )

                redis_client.hset(
                    task_id,
                    mapping={
                        "status":
                            "SUCCESS",

                        "stage":
                            "Completed",

                        "progress":
                            100,
                    },
                )

                print("REDIS:")

                print(
                    redis_client.hgetall(
                        task_id
                    )
                )

            print(
                "\n" + "=" * 70
            )

            print(
                "Repository Indexed Successfully"
            )

            print(
                "=" * 70
            )

            print(
                repository_profile
            )

            print(
                "=" * 70
            )

            return {
                "status":
                    "success",

                "files":
                    len(source_files),

                "chunks":
                    len(all_chunks),

                "repository_profile":
                    repository_profile,
            }

        except Exception as e:

            if task_id:

                redis_client.hset(
                    task_id,
                    mapping={
                        "status":
                            "FAILED",

                        "error":
                            str(e),
                    },
                )

                print("REDIS:")

                print(
                    redis_client.hgetall(
                        task_id
                    )
                )

            raise