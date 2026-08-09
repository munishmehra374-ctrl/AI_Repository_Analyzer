from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.prompts import ANSWER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService

class AnswerNode:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm = llm_service

    def __call__(
        self,
        state: GraphState,
    ):

        # =====================================================
        # Get Question
        # =====================================================

        question = state.get(
            "question",
            "",
        )

        question_type = state.get(
            "question_type",
            "general",
        )

        # =====================================================
        # Get Tool Contexts
        # =====================================================

        retrieval_context = (
            state.get("retrieval_context")
            or ""
        )

        graph_context = (
            state.get("graph_context")
            or ""
        )

        repository_context = (
            state.get("repository_context")
            or ""
        )

        # =====================================================
        # Build Final Context
        # =====================================================

        retrieval_context = (
            state.get("retrieval_context")
            or ""
        )

        graph_context = (
            state.get("graph_context")
            or ""
        )

        repository_context = (
            state.get("repository_context")
            or ""
        )

        context_parts = []

        if retrieval_context:
            context_parts.append(
                "===== RETRIEVAL CONTEXT =====\n"
                + retrieval_context
            )

        if graph_context:
            context_parts.append(
                "===== GRAPH CONTEXT =====\n"
                + graph_context
            )

        if repository_context:
            context_parts.append(
                "===== REPOSITORY CONTEXT =====\n"
                + repository_context
            )

        context = "\n\n".join(context_parts)

        # Store aggregated context

        state["context"] = context

        # =====================================================
        # Debug
        # =====================================================

        print("\n========== ANSWER NODE ==========")

        print("Question:")
        print(question)

        print("\nQuestion Type:")
        print(question_type)

        print(
            "\nRetrieval Context Length:",
            len(retrieval_context),
        )

        print(
            "Graph Context Length:",
            len(graph_context),
        )

        print(
            "Repository Context Length:",
            len(repository_context),
        )

        print(
            "FINAL CONTEXT LENGTH:",
            len(context),
        )

        print(
            "\n========== FINAL CONTEXT PREVIEW =========="
        )
        print(context[:10000])
        print(
            "============================================\n"
        )

        # =====================================================
        # Build Answer Prompt
        # =====================================================

        prompt = ANSWER_PROMPT.format(
            context=context,
            question_type=question_type,
        )

        # =====================================================
        # LLM Messages
        # =====================================================

        messages = [
            SystemMessage(
                content=prompt
            ),
            HumanMessage(
                content=question
            ),
        ]

        # =====================================================
        # Generate Answer
        # =====================================================

        answer = self.llm.invoke(
            messages
        )

        # =====================================================
        # Store Answer
        # =====================================================

        print("\n========== FINAL ANSWER ==========")
        print(answer)
        print("==================================\n")

        state["answer"] = answer

        return state