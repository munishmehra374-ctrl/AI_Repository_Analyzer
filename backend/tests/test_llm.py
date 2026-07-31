from app.graph.dependencies import dependencies

from app.graph.workflow import create_workflow

from app.services.indexing_service import IndexingService

repo_path = r"C:\Users\MUNISH MEHRA\OneDrive\Desktop\AI-Repository-Analyzer\backend\cloned_repos\fastapi"

indexing = IndexingService()

result = indexing.index_repository(repo_path)

dependencies.initialize(
    result["vector_store"],
    result["bm25_index"]
)

graph = create_workflow()

state = {
    "question": "How are routes defined in FastAPI?",

    "repository_uploaded": True,

    "repository_indexed": True,

    "repository_name": "fastapi",

    "primary_language": "python",

    "question_type": None,

    "needs_retrieval": True,

    "context": "",

    "answer": ""
}

response = graph.invoke(state)

print(response["answer"])