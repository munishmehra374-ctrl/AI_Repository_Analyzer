from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.core.config import get_settings
from app.graph.prompts import REVIEWER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class ReviewerNode:

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

        question_type = (
            state.get("question_type")
            or ""
        )

        analysis = (
            state.get("analysis")
            or ""
        )

        root_cause = (
            state.get("root_cause")
            or ""
        )

        is_security_question = (
            "security" in question_type.lower()
        )

        # ======================================================
        # Empty Security Result
        # ======================================================

        if (
            is_security_question
            and not root_cause.strip()
        ):

            result = self._empty_review()

            print(
                "\n" + "=" * 80
            )

            print(
                "REVIEWER AGENT"
            )

            print(
                "=" * 80
            )

            print(
                "\nSecurity & Architecture input is empty."
            )

            print(
                "\nREVIEW RESULT:"
            )

            print(
                result
            )

            print(
                "=" * 80 + "\n"
            )

            state["review"] = result

            return state

        # ======================================================
        # Security Questions
        # ======================================================
        #
        # IMPORTANT:
        #
        # For security questions, the Security Agent is the
        # authoritative source for security/architecture findings.
        #
        # Implementation analysis is provided separately only so
        # the reviewer can preserve valid implementation findings.
        #
        # The reviewer must NOT turn implementation observations
        # into security findings.
        # ======================================================

        if is_security_question:

            prompt = REVIEWER_PROMPT.format(
                question=question,
                question_type=question_type,
                analysis=analysis,
                root_cause=root_cause,
            )

        # ======================================================
        # Other Deep-Analysis Questions
        # ======================================================

        else:

            prompt = REVIEWER_PROMPT.format(
                question=question,
                question_type=question_type,
                analysis=analysis,
                root_cause=root_cause,
            )

        # ======================================================
        # Debug
        # ======================================================

        print(
            "\n" + "=" * 80
        )

        print(
            "REVIEWER AGENT"
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
            "\nQuestion Type:"
        )

        print(
            question_type
        )

        print(
            "\nSecurity Question:"
        )

        print(
            is_security_question
        )

        print(
            "\nAnalysis Length:"
        )

        print(
            len(analysis)
        )

        print(
            "\nSecurity & Architecture Length:"
        )

        print(
            len(root_cause)
        )

        print(
            "\nPrompt Length:"
        )

        print(
            len(prompt)
        )

        print(
            "\nConfigured Output Budget:"
        )

        print(
            self.settings.REVIEWER_MAX_OUTPUT_TOKENS
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
                HumanMessage(
                    content=question
                ),
            ],
            max_output_tokens=(
                self.settings.REVIEWER_MAX_OUTPUT_TOKENS
            ),
        )

        # ======================================================
        # Empty LLM Response
        # ======================================================

        if not result:

            result = self._empty_review()

        # ======================================================
        # Security Safety Check
        # ======================================================
        #
        # If the Security Agent explicitly returned no supported
        # security/architecture finding, do not allow the reviewer
        # to manufacture one from implementation analysis.
        # ======================================================

        if (
            is_security_question
            and self._security_result_has_no_finding(
                root_cause
            )
        ):

            result = self._empty_review()

            print(
                "\nSECURITY REVIEW GUARD:"
            )

            print(
                "Security Agent returned no supported "
                "security/architecture finding."
            )

        # ======================================================
        # Result
        # ======================================================

        print(
            "\nREVIEW RESULT:"
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

        state["review"] = result

        return state

    # ==========================================================
    # Check Whether Security Agent Has a Supported Finding
    # ==========================================================

    @staticmethod
    def _security_result_has_no_finding(
        root_cause: str,
    ) -> bool:

        if not root_cause.strip():
            return True

        normalized = (
            root_cause
            .strip()
            .lower()
        )

        # ------------------------------------------------------
        # JSON result produced by Security Agent
        # ------------------------------------------------------

        if (
            '"findings": []'
            in normalized
        ):
            return True

        # ------------------------------------------------------
        # Legacy / fallback representation
        # ------------------------------------------------------

        if (
            "security & architecture findings:"
            in normalized
            and "- no supported finding identified."
            in normalized
        ):
            return True

        return False

    # ==========================================================
    # Empty Review
    # ==========================================================

    @staticmethod
    def _empty_review() -> str:

        return (
            "IMPLEMENTATION FINDINGS:\n\n"
            "- No supported finding identified.\n\n"
            "SECURITY & ARCHITECTURE FINDINGS:\n\n"
            "- No supported finding identified.\n\n"
            "OVERALL CONCLUSION:\n\n"
            "- No confirmed security or architecture issue "
            "can be established from the provided repository context."
        )