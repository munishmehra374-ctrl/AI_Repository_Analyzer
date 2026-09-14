from app.retrieval.bm25_index import BM25Index
from app.services.chunk_service import ChunkService
from app.services.repository_reader import RepositoryReader
from app.vectorstore.chroma_store import ChromaStore

from app.knowledge.graph_service import GraphService
from app.services.repository_metadata_service import RepositoryMetadataService
from app.core.redis import redis_client
from app.graph.dependencies import dependencies

import json
import hashlib
from pathlib import Path

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
    # File Fingerprinting
    # =====================================================

    @staticmethod
    def _get_file_hash(file_path: str) -> str:

        with open(
            file_path,
            "rb",
        ) as f:

            return hashlib.sha256(
                f.read()
            ).hexdigest()


    @classmethod
    def _get_file_hashes(
        cls,
        source_files: list[str],
    ) -> dict[str, str]:

        return {
            str(file_path): cls._get_file_hash(
                file_path
            )
            for file_path in source_files
        }


    def _get_extracted_data_key(
        self,
        repository_id: str,
        file_path: str,
    ) -> str:

        return f"extracted:{repository_id}:{file_path}"


    def _save_extracted_data(
        self,
        repository_id: str,
        file_path: str,
        extracted_data: dict,
    ):

        redis_client.set(
            self._get_extracted_data_key(
                repository_id,
                file_path,
            ),
            json.dumps(extracted_data),
        )


    def _load_extracted_data(
        self,
        repository_id: str,
        file_path: str,
    ):

        data = redis_client.get(
            self._get_extracted_data_key(
                repository_id,
                file_path,
            )
        )

        if not data:
            return None

        if isinstance(data, bytes):
            data = data.decode("utf-8")

        return json.loads(data)

    # =====================================================
    # Repository Indexing
    # =====================================================

  

    def index_repository(
        self,
        repository_path: str,
        task_id=None,
        repository_id: str | None = None,
    ):

        self.metadata_service = RepositoryMetadataService()

        if not repository_id:
            raise ValueError(
                "repository_id is required for repository indexing."
        )

        print("INDEXING SERVICE STARTED")
        print("TASK ID:", task_id)

        source_files = self.repository_reader.get_source_files(
            repository_path
        )

        print("FOUND FILES:", len(source_files))

        # =====================================================
        # Incremental Indexing
        # =====================================================

        current_file_hashes = self._get_file_hashes(
            source_files
        )

# =====================================================
# Load Previous File Hashes
# =====================================================

        hash_key = f"file_hashes:{repository_id}"

        previous_hashes_raw = redis_client.get(
            hash_key
        )

        if previous_hashes_raw:

            if isinstance(previous_hashes_raw, bytes):
                previous_hashes_raw = (
                    previous_hashes_raw.decode("utf-8")
                )

            previous_file_hashes = json.loads(
                previous_hashes_raw
            )

        else:

            previous_file_hashes = {}


        # =====================================================
        # Detect Changed / New Files
        # =====================================================

        changed_files = []
        unchanged_files = []

        for file_path, current_hash in current_file_hashes.items():

            previous_hash = previous_file_hashes.get(
                file_path
            )

            if previous_hash == current_hash:

                unchanged_files.append(file_path)

            else:

                changed_files.append(file_path)


        print("\n========== INCREMENTAL INDEXING ==========")

        print(
            "TOTAL FILES:",
            len(current_file_hashes)
        )

        print(
            "CHANGED / NEW:",
            len(changed_files)
        )

        print(
            "UNCHANGED:",
            len(unchanged_files)
        )

        print("\nCHANGED / NEW FILES:")

        for file_path in changed_files:
            print("  ", file_path)

        print("\nUNCHANGED FILES:")

        for file_path in unchanged_files:
            print("  ", file_path)

        print("==========================================\n")

        print("\nCURRENT FILE HASHES:")
        for file_path, file_hash in current_file_hashes.items():
            print(file_path, "->", file_hash)

        if task_id:

            redis_client.hset(
                task_id,
                mapping={
                    "status": "STARTED",
                    "stage": "Reading Repository",
                    "progress": 5,
                    "repository_id": repository_id,
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

        # =====================================================
        # Load extracted data for unchanged files
        # =====================================================

        for file_path in unchanged_files:

            previous_data = self._load_extracted_data(
                repository_id=repository_id,
                file_path=file_path,
            )

            if previous_data is not None:

                previous_data["file_path"] = file_path
                previous_data["repository_path"] = repository_path
                previous_data["repository_id"] = repository_id
                previous_data["repository_name"] = (
                    repository_path.split("\\")[-1]
                )
                previous_data["language"] = "python"

                all_extracted_data.append(
                    previous_data
                )

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
                        "repository_id": repository_id,
                    },
                )

                print("REDIS:")
                print(
                    redis_client.hgetall(
                        task_id
                    )
                )

            for index, file_path in enumerate(
                changed_files
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

                extracted_data["repository_id"] = repository_id

                extracted_data[
                    "repository_name"
                ] = repository_path.split(
                    "\\"
                )[-1]

                extracted_data[
                    "language"
                ] = "python"

                # =============================================
            # Save extracted data for incremental graph
            # =============================================

                self._save_extracted_data(
                    repository_id=repository_id,
                    file_path=file_path,
                    extracted_data=extracted_data,
                )



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
                            / len(changed_files)
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
                                len(changed_files),
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
                        all_extracted_data,
                    repository_id=
                        repository_id,
                     changed_files=
                        changed_files,
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

            # -------------------------------------------------
            # Clear previous vector index
            # -------------------------------------------------

            self.vector_store.clear_files(
                repository_id,
                changed_files,
            )

            # -------------------------------------------------
            # Add only changed-file chunks
            # -------------------------------------------------

            changed_chunks = [
                chunk
                for chunk in all_chunks
                if chunk["file_path"] in changed_files
            ]

            print(
                "\n========== CHROMA INCREMENTAL DEBUG =========="
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
                "All chunks:",
                len(all_chunks),
            )

            print(
                "Changed chunks:",
                len(changed_chunks),
            )

            for chunk in changed_chunks:

                print(
                    "ADD:",
                    chunk["file_path"],
                    "|",
                    chunk["chunk_id"],
                )

            print(
                "=============================================="
            )

            self.vector_store.add_documents(
                changed_chunks,
                repository_id,
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
          # =================================================
          # Incremental BM25 Index
          # =================================================

            bm25_index_path = (
                Path("bm25_db")
                / repository_id
                / "bm25.pkl"
            )

            if not all_chunks:

                print(
                    "\n========== SKIPPING BM25 =========="
                )
                print(
                    "WARNING: all_chunks is empty."
                )

            else:

                if bm25_index_path.exists():

                    print(
                        "\n========== LOADING EXISTING BM25 =========="
                    )

                    self.bm25_index.load(
                        "bm25_db",
                        repository_id,
                    )

                    self.bm25_index.update_files(
                        chunks=all_chunks,
                        repository_id=repository_id,
                        changed_files=changed_files,
                    )

                else:

                    print(
                        "\n========== BUILDING INITIAL BM25 =========="
                    )

                    self.bm25_index.build_index(
                        all_chunks,
                        repository_id,
                    )

                self.bm25_index.save(
                    "bm25_db",
                    repository_id,
                )
            # =================================================
            # Initialize Retrieval Pipeline
            # =================================================

            dependencies.initialize(
                vector_store=self.vector_store,
                bm25_index=self.bm25_index,
                repository_id=repository_id,
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
                    .build_from_extracted_data(
                        extracted_files=all_extracted_data,
                        repository_path=repository_path,
                    )
                )

            # =================================================
            # Save Repository Profile
            # =================================================

            if task_id:

                profile_data = {
                    **repository_profile,
                    "source_files": source_files,
                    "repository_id": repository_id,
                }

                redis_client.set(
                    f"profile:{task_id}",
                    json.dumps(profile_data),
                )

                redis_client.set(
                    f"profile:repository:{repository_id}",
                    json.dumps(profile_data)
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

                        "repository_id": 
                           repository_id,
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

            # =====================================================
            # Save Current File Hashes
            # =====================================================

            redis_client.set(
                hash_key,
                json.dumps(
                    current_file_hashes
                )
            )

            print(
                "FILE HASHES SAVED:",
                hash_key
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

                "repository_id": 
                     repository_id,
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