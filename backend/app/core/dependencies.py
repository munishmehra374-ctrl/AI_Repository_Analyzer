# from app.services.indexing_service import IndexingService
# from app.services.llm_service import LLMService
# from app.services.retrieval_service import RetrievalService

# from app.vectorstore.retriever import RepositoryRetriever
# from app.retrieval.bm25_retriever import BM25Retriever
# from app.retrieval.hybrid_retriever import HybridRetriever
# from app.retrieval.rrf import ReciprocalRankFusion
# from app.retrieval.reranker import CrossEncoderReranker
# from app.retrieval.context_optimizer import ContextOptimizer


# def create_services(repository_path: str):

#     indexing_service = IndexingService()

#     result = indexing_service.index_repository(repository_path)

#     repository_retriever = RepositoryRetriever(
#         result["vector_store"]
#     )

#     bm25_retriever = BM25Retriever(
#         result["bm25_index"]
#     )

#     hybrid_retriever = HybridRetriever(
#         repository_retriever,
#         bm25_retriever,
#     )

#     retrieval_service = RetrievalService(
#         hybrid_retriever,
#         ReciprocalRankFusion(),
#         CrossEncoderReranker(),
#         ContextOptimizer(),
#     )

#     llm_service = LLMService()

#     return {
#         "llm_service": llm_service,
#         "retrieval_service": retrieval_service,
#     }