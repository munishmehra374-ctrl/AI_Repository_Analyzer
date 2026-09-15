from app.core.config import get_settings
from app.core.llm_factory import LLMFactory

from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.repository_metadata_service import RepositoryMetadataService
from app.services.context_selection_service import (
    ContextSelectionService,
)

from app.vectorstore.retriever import RepositoryRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.rrf import ReciprocalRankFusion
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.context_optimizer import ContextOptimizer

from app.knowledge.graph_queries import GraphQueries
from app.knowledge.entity_resolver import EntityResolver

from app.tools.retrieval_tool import RetrievalTool
from app.tools.graph_tool import GraphTool
from app.tools.repository_tool import RepositoryTool


class DependencyContainer:

    def __init__(self):

        settings = get_settings()

        llm = LLMFactory.create()

        # ---------------------------------------------------------
        # Token counters
        # ---------------------------------------------------------

        def count_text_tokens(text: str) -> int:
            return llm.get_num_tokens(text)

        def count_message_tokens(messages) -> int:
            return llm.get_num_tokens_from_messages(
                messages
            )

        # ---------------------------------------------------------
        # Token budgets
        # ---------------------------------------------------------

        self._request_token_budget = (
            settings.REQUEST_TOKEN_BUDGET
        )

        self._context_token_budget = (
            settings.CONTEXT_TOKEN_BUDGET
        )

        self._output_token_reserve = (
            settings.OUTPUT_TOKEN_RESERVE
        )

        self._count_text_tokens = (
            count_text_tokens
        )

        self._count_message_tokens = (
            count_message_tokens
        )

        # ---------------------------------------------------------
        # LLM Service
        # ---------------------------------------------------------

        self.llm_service = LLMService(
            llm=llm,
            request_token_budget=(
                self._request_token_budget
            ),
            token_counter=(
                self._count_message_tokens
            ),
            output_token_reserve=(
                self._output_token_reserve
            ),
        )

        # ---------------------------------------------------------
        # Global Context Selection
        # ---------------------------------------------------------

        self.context_selection_service = ContextSelectionService(
                token_counter_fn=self._count_text_tokens
            )

        # ---------------- Services ----------------

        self.retrieval_service = None
        self.retrieval_services = {}

        self.repository_metadata_service = None

        # ---------------- Knowledge ----------------

        self.graph_queries = None

        # ---------------- Tools ----------------

        self.retrieval_tool = None
        self.retrieval_tools = {}

        self.graph_tool = None
        self.graph_tools = {}

        self.repository_tool = None

    def calculate_available_context_budget(
        self, system_prompt: str, question: str, chat_history_text: str = ""
    ) -> int:
        """Dynamically calculates the exact token budget left for context selection."""
        prompt_str = f"{system_prompt}\n{chat_history_text}\n{question}"
        prompt_tokens = self._count_text_tokens(prompt_str)
        
        # Available Budget = Request Cap - Prompt Overhead - Reserved Output
        available_budget = (
            self._request_token_budget - prompt_tokens - self._output_token_reserve
        )
        return max(0, available_budget)

    @property
    def count_text_tokens_fn(self):
        return self._count_text_tokens

    def initialize(
        self,
        vector_store,
        bm25_index,
        repository_id: str,
    ):

        # ---------------------------------------------------------
        # Knowledge
        # ---------------------------------------------------------

        self.graph_queries = GraphQueries()

        entity_resolver = EntityResolver(
            self.graph_queries,
            repository_id=repository_id,
        )

        # ---------------------------------------------------------
        # Retrieval
        # ---------------------------------------------------------

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

            # Existing logic unchanged
            rrf=ReciprocalRankFusion(),

            reranker=CrossEncoderReranker(),

            context_optimizer=ContextOptimizer(
                max_chunks=3,
                context_token_budget=(
                    self._context_token_budget
                ),
                token_counter=(
                    self._count_text_tokens
                ),
            ),

            entity_resolver=entity_resolver,
        )

        self.retrieval_services[
            repository_id
        ] = self.retrieval_service

        # ---------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------

        self.repository_metadata_service = (
            RepositoryMetadataService()
        )

        # ---------------------------------------------------------
        # Tools
        # ---------------------------------------------------------

        self.retrieval_tool = RetrievalTool(
            self.retrieval_service
        )

        self.retrieval_tools[
            repository_id
        ] = self.retrieval_tool

        # ---------------------------------------------------------
        # Repository-specific Graph Tool
        # ---------------------------------------------------------

        self.graph_tool = GraphTool(
            self.graph_queries,
            repository_id,
        )

        self.graph_tools[
            repository_id
        ] = self.graph_tool

        # ---------------------------------------------------------
        # Repository Tool
        # ---------------------------------------------------------

        self.repository_tool = RepositoryTool(
            self.repository_metadata_service
        )

    def get_retrieval_service(
        self,
        repository_id: str,
    ):
        return self.retrieval_services.get(
            repository_id
        )

    def get_retrieval_tool(
        self,
        repository_id: str,
    ):
        return self.retrieval_tools.get(
            repository_id
        )

    def get_graph_tool(
        self,
        repository_id: str,
    ):
        return self.graph_tools.get(
            repository_id
        )


dependencies = DependencyContainer()