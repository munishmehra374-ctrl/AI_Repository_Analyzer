from langchain_core.messages import SystemMessage

from app.core.config import get_settings
from app.graph.prompts import ANALYSIS_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class AnalysisNode:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm = llm_service
        self.settings = get_settings()

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        question = state["question"]

        context = (
            state.get("context")
            or ""
        )

        # ======================================================
        # Build Analysis Prompt
        # ======================================================

        prompt = ANALYSIS_PROMPT.format(
            question=question,
            context=context,
        )

        # ======================================================
        # Debug
        # ======================================================

        print(
            "\n" + "=" * 80
        )

        print(
            "ANALYSIS AGENT"
        )

        print(
            "=" * 80
        )

        print(
            "\nQuestion:"
        )

        print(
            question
        )

        print(
            "\nContext characters:"
        )

        print(
            len(context)
        )

        print(
            "\nConfigured output budget:"
        )

        print(
            self.settings.ANALYSIS_MAX_OUTPUT_TOKENS
        )

        print(
            "\nPrompt characters:"
        )

        print(
            len(prompt)
        )

        print(
            "=" * 80
        )

        # ======================================================
        # LLM Call
        # ======================================================

        result = self.llm.invoke(
            [
                SystemMessage(
                    content=prompt
                ),
            ],
            max_output_tokens=(
                self.settings.ANALYSIS_MAX_OUTPUT_TOKENS
            ),
        )

        # ======================================================
        # Result
        # ======================================================

        print(
            "\nANALYSIS RESULT:"
        )

        print(
            result
        )

        print(
            "=" * 80 + "\n"
        )

        # ======================================================
        # Store Result
        # ======================================================
        
        return {
            "analysis": result,
        }