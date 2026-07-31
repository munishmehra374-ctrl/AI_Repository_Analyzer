from __future__ import annotations

from app.graph.state import GraphState
from app.services.retrieval_service import RetrievalService


class RetrievalNode:
    """
    LangGraph node responsible for retrieving relevant
    repository context for the user's question.
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
    ) -> None:

        self._retrieval_service = retrieval_service

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        # Skip retrieval if the planner determined it is unnecessary
        if not state["needs_retrieval"]:
            state["context"] = ""
            return state

        context = self._retrieval_service.retrieve(
            state["question"]
        )

        state["context"] = context

        return state