from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.core.config import get_settings
from app.graph.prompts import ANSWER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class AnswerNode:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm = llm_service
        self.settings = get_settings()

    # ==========================================================
    # Build messages for final answer
    # ==========================================================

    def build_messages(
        self,
        question: str,
        question_type: str,
        context: str,
    ):

        prompt = ANSWER_PROMPT.format(
            context=context,
            question_type=question_type,
        )

        return [
            SystemMessage(
                content=prompt
            ),
            HumanMessage(
                content=question
            ),
        ]

    # ==========================================================
    # Build messages WITHOUT repository context
    # ==========================================================

    def build_messages_without_context(
        self,
        question: str,
        question_type: str,
    ):

        return self.build_messages(
            question=question,
            question_type=question_type,
            context="",
        )

    # ==========================================================
    # Node
    # ==========================================================

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        question = state.get(
            "question",
            "",
        )

        question_type = state.get(
            "question_type",
            "general",
        )

        deep_analysis = state.get(
            "deep_analysis",
            False,
        )

        # ======================================================
        # NORMAL QUESTIONS
        # ======================================================

        if not deep_analysis:

            context = (
                state.get("context")
                or ""
            )

        # ======================================================
        # MULTI-AGENT QUESTIONS
        # ======================================================

        else:

            review = (
                state.get("review")
                or ""
            )

            context = (
                "===== REVIEWED MULTI-AGENT ANALYSIS =====\n\n"
                + review
            )

        # ======================================================
        # Deterministic Security Guard
        # ======================================================

        is_security_question = (
            "security" in question_type.lower()
        )

        if (
            deep_analysis
            and is_security_question
            and self._has_no_supported_finding(
                context
            )
        ):

            answer = (
                "No confirmed security or architecture issue "
                "can be established from the provided repository context."
            )

            print(
                "\n========== ANSWER NODE =========="
            )

            print(
                "Question:"
            )

            print(
                question
            )

            print(
                "\nQuestion Type:"
            )

            print(
                question_type
            )

            print(
                "\nDeep Analysis:"
            )

            print(
                deep_analysis
            )

            print(
                "\nDeterministic Security Guard:"
            )

            print(
                "No supported security finding detected."
            )

            print(
                "\nFINAL ANSWER:"
            )

            print(
                answer
            )

            print(
                "==================================\n"
            )

            state["answer"] = answer

            return state

        # ======================================================
        # Debug
        # ======================================================

        print(
            "\n========== ANSWER NODE =========="
        )

        print(
            "Question:"
        )

        print(
            question
        )

        print(
            "\nQuestion Type:"
        )

        print(
            question_type
        )

        print(
            "\nDeep Analysis:"
        )

        print(
            deep_analysis
        )

        print(
            "\nFinal Context Length:"
        )

        print(
            len(context)
        )

        print(
            "\nConfigured Output Budget:"
        )

        print(
            self.settings.ANSWER_MAX_OUTPUT_TOKENS
        )

        print(
            "\n========== FINAL CONTEXT PREVIEW =========="
        )

        print(
            context[:10000]
        )

        print(
            "============================================\n"
        )

        # ======================================================
        # Build final messages
        # ======================================================

        messages = self.build_messages(
            question=question,
            question_type=question_type,
            context=context,
        )

        # ======================================================
        # Generate Answer
        # ======================================================

        answer = self.llm.invoke(
            messages,
            max_output_tokens=(
                self.settings.ANSWER_MAX_OUTPUT_TOKENS
            ),
        )

        # ======================================================
        # Store Answer
        # ======================================================

        print(
            "\n========== FINAL ANSWER =========="
        )

        print(
            answer
        )

        print(
            "==================================\n"
        )

        state["answer"] = answer

        return state

    # ==========================================================
    # Security Finding Check
    # ==========================================================

    @staticmethod
    def _has_no_supported_finding(
        context: str,
    ) -> bool:

        normalized = (
            context
            .strip()
            .lower()
        )

        if not normalized:
            return True

        security_header = (
            "security & architecture findings:"
        )

        no_finding_marker = (
            "- no supported finding identified."
        )

        overall_conclusion = (
            "no confirmed security or architecture issue "
            "can be established from the provided repository context."
        )

        if (
            security_header in normalized
            and no_finding_marker in normalized
            and overall_conclusion in normalized
        ):
            return True

        return False