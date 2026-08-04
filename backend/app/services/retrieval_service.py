from __future__ import annotations

from app.retrieval.context_optimizer import ContextOptimizer
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.reranker import CrossEncoderReranker
from app.retrieval.rrf import ReciprocalRankFusion


class RetrievalService:
    """
    Orchestrates the complete retrieval pipeline.
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

        print("\n========== RETRIEVAL SERVICE ==========")
        print("Question:", question)

        # -----------------------------------------
        # Step 1 : Hybrid Retrieval
        # -----------------------------------------

        results = self._hybrid_retriever.retrieve(question)

        vector_results = results["vector_results"]
        bm25_results = results["bm25_results"]

        print(f"\nVector Results : {len(vector_results)}")
        print(f"BM25 Results   : {len(bm25_results)}")

        if vector_results:
            print("\nFirst Vector Result:")
            print(vector_results[0])

        if bm25_results:
            print("\nFirst BM25 Result:")
            print(bm25_results[0])

        # -----------------------------------------
        # Step 2 : Reciprocal Rank Fusion
        # -----------------------------------------

        fused_results = self._rrf.fuse(
            vector_results=vector_results,
            bm25_results=bm25_results,
        )

        print(f"\nFused Results : {len(fused_results)}")

        # -----------------------------------------
        # Step 3 : Cross Encoder Re-ranking
        # -----------------------------------------

        reranked_results = self._reranker.rerank(
            query=question,
            chunks=fused_results,
        )

        print(f"Reranked Results : {len(reranked_results)}")

        # -----------------------------------------
        # Step 4 : Context Optimization
        # -----------------------------------------

        optimized_context = self._context_optimizer.optimize(
            reranked_results
        )

        print(f"Optimized Chunks : {len(optimized_context)}")

        # -----------------------------------------
        # Step 5 : Final Context
        # -----------------------------------------

        context = "\n\n".join(
            chunk["code"]
            for chunk in optimized_context
        )

        print("\n========== FINAL RETRIEVAL CONTEXT ==========")
        print(context[:1000])
        print("=============================================\n")

        return context