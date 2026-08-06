from fastapi import APIRouter

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

router = APIRouter(
    prefix="/repositories",
    tags=["Repositories"]
)

clone_service = CloneService()
parser_service = ParserService()
extractor_service = ExtractorService()
chunk_service = ChunkService()
indexing_service = IndexingService()

repository_retriever = RepositoryRetriever(
    indexing_service.vector_store
)


@router.post("/clone")
def clone_repository(request: RepositoryRequest):
    return clone_service.clone_repository(request.url)


@router.get("/parse")
def parse_file(file_path: str):

    tree = parser_service.parse_file(file_path)

    return {
        "root_node": tree.root_node.type,
        "children": len(tree.root_node.children)
    }


@router.get("/extract")
def extract(file_path: str):

    return extractor_service.extract(file_path)


@router.get("/chunks")
def generate_chunks(file_path: str):

    return chunk_service.generate_chunks(file_path)

@router.post("/index")
def index_file(file_path: str):

    task = index_repository_task.delay(file_path)

    return {
        "task_id": task.id,
        "status": "queued"
    }

@router.get("/status/{task_id}")
def get_task_status(task_id: str):

    task = AsyncResult(task_id, app=celery)

    response = {
        "task_id": task.id,
        "status": task.status,
    }

    if task.successful():
        response["result"] = task.result

    elif task.failed():
        response["error"] = str(task.result)

    return response

@router.get("/progress/{task_id}")
def get_progress(task_id: str):
 
    progress = redis_client.hgetall(task_id)

    if not progress:
        return {
            "message": "Task not found"
        }

    return progress


@router.get("/search")
def search(question: str):

    documents = repository_retriever.retrieve(
        question
    )

    return documents

@router.post("/chat")
def chat(question: str):

    if dependencies.retrieval_service is None:
        return {
            "error": "Repository not indexed. Please call /repositories/index first."
        }

    workflow = create_workflow()

    result = workflow.invoke(
        {
            "question": question,
            "repository_uploaded": True,
            "repository_indexed": True,
            "repository_name": "AI-Repository-Analyzer",
            "primary_language": "Python",
            "question_type": None,
            "needs_retrieval": True,
            "context": "",
            "answer": "",
        }
    )

    return result["answer"]