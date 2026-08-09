from fastapi import APIRouter
import json
import uuid

from app.models.repository import RepositoryRequest

from app.services.clone_service import CloneService
from app.services.parser_service import ParserService
from app.services.extractor_service import ExtractorService
from app.services.chunk_service import ChunkService
from app.services.indexing_service import IndexingService

from app.vectorstore.chroma_store import ChromaStore
from app.vectorstore.retriever import RepositoryRetriever

from app.graph.workflow import create_workflow
from app.graph.dependencies import dependencies

from app.worker.indexing_tasks import index_repository_task

from celery.result import AsyncResult
from app.worker.celery_app import celery

from app.core.redis import redis_client

from app.retrieval.bm25_index import BM25Index

from app.knowledge.graph_queries import GraphQueries


router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"],
)


clone_service = CloneService()
parser_service = ParserService()
extractor_service = ExtractorService()
chunk_service = ChunkService()
indexing_service = IndexingService()
graph_queries = GraphQueries()


repository_retriever = RepositoryRetriever(
    indexing_service.vector_store
)


# =====================================================
# Clone Repository
# =====================================================

@router.post("/clone")
def clone_repository(
    request: RepositoryRequest,
):

    return clone_service.clone_repository(
        request.url
    )


# =====================================================
# Parse File
# =====================================================

@router.get("/parse")
def parse_file(
    file_path: str,
):

    tree = parser_service.parse_file(
        file_path
    )

    return {
        "root_node": tree.root_node.type,
        "children": len(
            tree.root_node.children
        ),
    }


# =====================================================
# Extract
# =====================================================

@router.get("/extract")
def extract(
    file_path: str,
):

    return extractor_service.extract(
        file_path
    )


# =====================================================
# Generate Chunks
# =====================================================

@router.get("/chunks")
def generate_chunks(
    file_path: str,
):

    return chunk_service.generate_chunks(
        file_path
    )


# =====================================================
# Index Repository
# =====================================================

@router.post("/index")
def index_file(
    file_path: str,
):

    # Generate ONE task ID.
    # This exact ID is sent to Celery and returned
    # to the frontend.

    task_id = str(
        uuid.uuid4()
    )

    task = index_repository_task.apply_async(
        args=[file_path],
        task_id=task_id,
    )

    print("=" * 80)
    print("FASTAPI TASK ID:", task.id)
    print("GENERATED TASK ID:", task_id)
    print("=" * 80)

    return {
        "task_id": task_id,
        "status": "queued",
    }


# =====================================================
# Task Status
# =====================================================

@router.get("/status/{task_id}")
def get_task_status(
    task_id: str,
):

    task = AsyncResult(
        task_id,
        app=celery,
    )

    response = {
        "task_id": task.id,
        "status": task.status,
    }

    if task.successful():

        response["result"] = task.result

    elif task.failed():

        response["error"] = str(
            task.result
        )

    return response


# =====================================================
# Progress
# =====================================================

@router.get("/progress/{task_id}")
def get_progress(
    task_id: str,
):

    print("\n" + "=" * 80)
    print("GET PROGRESS CALLED")
    print("TASK ID:", task_id)

    try:

        progress = redis_client.hgetall(
            task_id
        )

        print("HGETALL RESULT:")
        print(progress)

    except Exception as e:

        print(
            "ERROR READING REDIS:",
            e,
        )

        progress = {}

    print("=" * 80 + "\n")

    # -------------------------------------------------
    # Redis progress exists
    # -------------------------------------------------

    if progress:

        return progress

    # -------------------------------------------------
    # Redis progress does not exist
    # Check Celery directly
    # -------------------------------------------------

    task = AsyncResult(
        task_id,
        app=celery,
    )

    print(
        "CELERY TASK STATUS:",
        task.status,
    )

    if task.status == "PENDING":

        return {
            "task_id": task_id,
            "status": "PENDING",
            "stage": "Queued",
            "progress": "0",
            "files_processed": "0",
            "total_files": "0",
        }

    if task.status == "SUCCESS":

        return {
            "task_id": task_id,
            "status": "SUCCESS",
            "stage": "Repository Indexed",
            "progress": "100",
        }

    if task.status == "FAILURE":

        return {
            "task_id": task_id,
            "status": "FAILED",
            "stage": "Indexing Failed",
            "progress": "0",
            "error": str(
                task.result
            ),
        }

    return {
        "task_id": task_id,
        "status": task.status,
        "stage": "Processing",
        "progress": "0",
    }


# =====================================================
# Repository Profile
# =====================================================

@router.get("/profile/{task_id}")
def get_repository_profile(
    task_id: str,
):

    profile = redis_client.get(
        f"profile:{task_id}"
    )

    if profile is None:

        return {
            "error": "Repository profile not found."
        }

    return json.loads(
        profile
    )

# =====================================================
# Knowledge Graph Statistics
# =====================================================

@router.get("/graph/statistics")
def get_graph_statistics():

    return graph_queries.get_graph_statistics()


# =====================================================
# Knowledge Graph Dependencies
# =====================================================

@router.get("/graph/dependencies")
def get_graph_dependencies():

    return graph_queries.get_dependency_graph()


# =====================================================
# Search
# =====================================================

@router.get("/search")
def search(
    question: str,
):

    documents = repository_retriever.retrieve(
        question
    )

    return documents


# =====================================================
# Chat
# =====================================================

@router.post("/chat")
def chat(
    question: str,
):

    print("=" * 60)
    print("FASTAPI Retrieval Service:")
    print(
        dependencies.retrieval_service
    )
    print("=" * 60)

    # Initialize retrieval pipeline
    # if it hasn't been created.

    if dependencies.retrieval_service is None:

        print(
            "Initializing Retrieval Pipeline..."
        )

        vector_store = ChromaStore()

        bm25_index = BM25Index()

        bm25_index.load(
            "bm25_db"
        )

        dependencies.initialize(
            vector_store=vector_store,
            bm25_index=bm25_index,
        )

        print(
            "Retrieval Pipeline Initialized!"
        )

        print(
            dependencies.retrieval_service
        )

    workflow = create_workflow()

    result = workflow.invoke(
        {
            "question": question,

            "repository_uploaded": True,

            "repository_indexed": True,

            "repository_name":
                "AI-Repository-Analyzer",

            "primary_language":
                "Python",

            "question_type": None,

            "tools": [],

            "reason": None,

            "retrieval_context": None,

            "graph_context": None,

            "repository_context": None,

            "needs_retrieval": True,

            "context": "",

            "answer": "",
        }
    ) 

    return {
        "answer": result["answer"]
    }