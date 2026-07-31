from __future__ import annotations

from app.retrieval.context_optimizer import ContextOptimizer
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.rrf import ReciprocalRankFusion


class RetrievalService:
    """
    Orchestrates the complete retrieval pipeline.

    Pipeline
    --------
    Hybrid Retrieval
            ↓
    Reciprocal Rank Fusion
            ↓
    Cross Encoder Re-ranking
            ↓
    Context Optimization
            ↓
    Final Context
    """

    def __init__(
        self,
        hybrid_retriever: HybridRetriever,
        rrf: ReciprocalRankFusion,
        reranker: CrossEncoderReranker,
        context_optimizer: ContextOptimizer,
    ) -> None:

        self._hybrid_retriever = hybrid_retriever
        self._rrf = rrf
        self._reranker = reranker
        self._context_optimizer = context_optimizer

    def retrieve(
        self,
        question: str,
    ) -> str:
        """
        Execute the complete retrieval pipeline.
        """

        # Step 1 : Hybrid Retrieval
        results = self._hybrid_retriever.retrieve(question)

        vector_results = results["vector_results"]
        bm25_results = results["bm25_results"]

        print("\n========== VECTOR ==========")
        print(vector_results[0])

        print("\n========== BM25 ==========")
        print(bm25_results[0])

        # Step 2 : Reciprocal Rank Fusion
        fused_results = self._rrf.fuse(
            vector_results=vector_results,
            bm25_results=bm25_results,
        )

        # Step 3 : Cross Encoder Re-ranking
        reranked_results = self._reranker.rerank(
            query=question,
            chunks=fused_results,
        )

        # Step 4 : Context Optimization
        optimized_context = self._context_optimizer.optimize(
            reranked_results
        )

        # Step 5 : Convert chunks into a single context string
        context = "\n\n".join(
            chunk["code"]
            for chunk in optimized_context
        )

        return context