from app.core.llm_factory import LLMFactory

from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.repository_metadata_service import RepositoryMetadataService

from app.vectorstore.retriever import RepositoryRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.rrf import ReciprocalRankFusion
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.context_optimizer import ContextOptimizer

from app.knowledge.graph_queries import GraphQueries

from app.tools.retrieval_tool import RetrievalTool
from app.tools.graph_tool import GraphTool
from app.tools.repository_tool import RepositoryTool


class DependencyContainer:

    def __init__(self):

        llm = LLMFactory.create()

        self.llm_service = LLMService(llm)

        # ---------------- Services ----------------

        self.retrieval_service = None
        self.repository_metadata_service = None

        # ---------------- Knowledge ----------------

        self.graph_queries = None

        # ---------------- Tools ----------------

        self.retrieval_tool = None
        self.graph_tool = None
        self.repository_tool = None

    def initialize(self, vector_store, bm25_index):

        repository_retriever = RepositoryRetriever(
            vector_store
        )

        bm25_retriever = BM25Retriever(
            bm25_index
        )

        hybrid_retriever = HybridRetriever(
            repository_retriever,
            bm25_retriever,
        )

        self.retrieval_service = RetrievalService(
            hybrid_retriever=hybrid_retriever,
            rrf=ReciprocalRankFusion(),
            reranker=CrossEncoderReranker(),
            context_optimizer=ContextOptimizer(  max_chunks=2),
        )

        # ---------------- Knowledge ----------------

        self.graph_queries = GraphQueries()

        # ---------------- Metadata ----------------

        self.repository_metadata_service = RepositoryMetadataService()

        # ---------------- Tools ----------------

        self.retrieval_tool = RetrievalTool(
            self.retrieval_service
        )

        self.graph_tool = GraphTool(
            self.graph_queries
        )

        self.repository_tool = RepositoryTool(
            self.repository_metadata_service
        )


dependencies = DependencyContainer()