from app.core.llm_factory import LLMFactory

from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService

from app.vectorstore.retriever import RepositoryRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.rrf import ReciprocalRankFusion
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.context_optimizer import ContextOptimizer


class DependencyContainer:

    def __init__(self):

        llm = LLMFactory.create()

        self.llm_service = LLMService(llm)

        self.retrieval_service = None

    def initialize(self, vector_store, bm25_index):

        repository_retriever = RepositoryRetriever(
            vector_store
        )

        bm25_retriever = BM25Retriever(
            bm25_index
        )

        hybrid_retriever = HybridRetriever(
            repository_retriever,
            bm25_retriever
        )

        self.retrieval_service = RetrievalService(
            hybrid_retriever,
            ReciprocalRankFusion(),
            CrossEncoderReranker(),
            ContextOptimizer()
        )


dependencies = DependencyContainer()