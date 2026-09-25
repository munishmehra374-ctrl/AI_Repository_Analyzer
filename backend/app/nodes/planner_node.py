import json
import logging
from typing import Any

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.core.config import get_settings
from app.graph.prompts import PLANNER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


logger = logging.getLogger(__name__)


class PlannerNode:

    # Tools that the planner is allowed to select.
    ALLOWED_TOOLS = {
        "retrieval",
        "graph",
        "repository",
    }

    # Number of times to retry after an invalid/empty response.
    MAX_RETRIES = 2

    def __init__(
        self,
        llm_service: LLMService,
        entity_resolver: Any = None,
    ):
        self.llm = llm_service
        self.entity_resolver = entity_resolver
        self.settings = get_settings()

    def __call__(
        self,
        state: GraphState,
    ):

        question = state.get("question", "")

        # ======================================================
        # Symbol-Aware Pre-Resolution
        # ======================================================
        resolved_entity = None
        if self.entity_resolver:
            try:
                resolved_entity = self.entity_resolver.resolve(question)
            except Exception as e:
                logger.warning("EntityResolver failed in PlannerNode: %s", e)
                resolved_entity = None

        symbol_hint = ""
        if resolved_entity and resolved_entity.get("name"):
            entity_name = resolved_entity["name"]
            entity_type = resolved_entity.get("type", "entity")
            symbol_hint = (
                f"\n\n==============================================================\n"
                f"DETECTED REPOSITORY SYMBOL:\n"
                f"The question references '{entity_name}' (type: {entity_type}),\n"
                f"which has been verified to exist in this repository's codebase.\n"
                f"Treat this as a repository question (do NOT classify as 'general').\n"
                f"Select appropriate repository tool(s) such as 'retrieval' or 'graph'.\n"
                f"==============================================================\n"
            )
            print(
                f"\n[SYMBOL-AWARE ROUTER] Verified repository {entity_type}: '{entity_name}'"
            )

        prompt = PLANNER_PROMPT.format(
            repository_uploaded=state["repository_uploaded"],
            repository_indexed=state["repository_indexed"],
            repository_name=state["repository_name"],
            primary_language=state["primary_language"],
            question=question,
        ) + symbol_hint

        print("\n" + "=" * 80)
        print("PLANNER NODE")
        print("=" * 80)

        print("Question:")
        print(state["question"])

        # ======================================================
        # Planner LLM Call
        # ======================================================

        response = None
        decision = None

        for attempt in range(
            1,
            self.MAX_RETRIES + 1,
        ):

            print(
                f"\nPLANNER ATTEMPT: "
                f"{attempt}/{self.MAX_RETRIES}"
            )

            try:

                # On retry, make the JSON requirement even more explicit.
                current_prompt = prompt

                if attempt > 1:

                    current_prompt = (
                        prompt
                        + """

IMPORTANT:
Your previous response was invalid or empty.

Return ONLY a valid JSON object.
Do not use Markdown.
Do not use ```json.
Do not explain your answer.

Required JSON structure:

{
  "question_type": "string",
  "tools": ["retrieval", "graph", "repository"],
  "reason": "string",
  "deep_analysis": true
}
"""
                    )

                response = self.llm.invoke(
                    [
                        SystemMessage(
                            content=current_prompt
                        ),
                        HumanMessage(
                            content=state["question"]
                        ),
                    ],
                    max_output_tokens=(
                        self.settings.PLANNER_MAX_OUTPUT_TOKENS
                    ),
                )

                print("\nRAW RESPONSE:")
                print(repr(response))

                # ==================================================
                # Validate response exists
                # ==================================================

                if not response:

                    logger.warning(
                        "Planner returned an empty response."
                    )

                    continue

                # LLMService normally returns a string.
                # Convert defensively in case another implementation
                # returns an object.
                response_text = str(response).strip()

                if not response_text:

                    logger.warning(
                        "Planner returned an empty string."
                    )

                    continue

                # ==================================================
                # Clean JSON response
                # ==================================================

                response_text = self._clean_json_response(
                    response_text
                )

                print("\nCLEANED RESPONSE:")
                print(response_text)

                if not response_text:

                    logger.warning(
                        "Planner response became empty "
                        "after cleaning."
                    )

                    continue

                # ==================================================
                # Parse JSON
                # ==================================================

                decision = json.loads(
                    response_text
                )

                # ==================================================
                # Validate planner decision
                # ==================================================

                self._validate_decision(
                    decision
                )

                # Successfully parsed and validated.
                break

            except json.JSONDecodeError as e:

                logger.warning(
                    "Planner returned invalid JSON "
                    "on attempt %s: %s",
                    attempt,
                    e,
                )

                decision = None

            except Exception as e:

                logger.exception(
                    "Planner attempt %s failed.",
                    attempt,
                )

                decision = None

        # ======================================================
        # Fail safely after retries
        # ======================================================

        if decision is None:

            raise ValueError(
                "Planner failed to produce a valid JSON decision "
                f"after {self.MAX_RETRIES} attempts."
            )

        print("\nPARSED DECISION:")
        print(decision)

        # ======================================================
        # Store Planner Decision
        # ======================================================

        state["question_type"] = (
            decision.get(
                "question_type",
                "repository",
            )
        )

        state["reason"] = (
            decision.get(
                "reason",
                "",
            )
        )

        state["deep_analysis"] = bool(
            decision.get(
                "deep_analysis",
                False,
            )
        )

        # ======================================================
        # Normalize Planner Tool Selection
        # ======================================================

        tools = decision.get(
            "tools",
            [],
        )

        if not isinstance(
            tools,
            list,
        ):
            tools = []

        # Keep only supported tools.
        tools = [
            tool
            for tool in tools
            if isinstance(tool, str)
            and tool in self.ALLOWED_TOOLS
        ]

        # Remove duplicates while preserving order.
        tools = list(
            dict.fromkeys(tools)
        )

        # ======================================================
        # Deep Analysis Retrieval Invariant
        # ======================================================
        #
        # Deep analysis requires actual repository source
        # evidence. Therefore retrieval must always be available.
        # ======================================================

        if state["deep_analysis"]:

            if "retrieval" not in tools:

                tools.append(
                    "retrieval"
                )

        # ======================================================
        # Symbol-Aware Routing Guardrail
        # ======================================================
        # If the question references a verified symbol in this repository,
        # ensure repository tools are selected so it never fails into 'tools: []'.
        # ======================================================
        if resolved_entity and resolved_entity.get("name"):
            if not tools or state["question_type"] == "general":
                print(
                    f"\n[SYMBOL-AWARE GUARD] Overriding empty/general tool selection "
                    f"for verified {resolved_entity.get('type', 'entity')} '{resolved_entity['name']}'."
                )
                if "retrieval" not in tools:
                    tools.append("retrieval")
                if state["question_type"] == "general":
                    state["question_type"] = (
                        "code"
                        if resolved_entity.get("type") in ("class", "function")
                        else "repository"
                    )

        state["tools"] = tools

        # ======================================================
        # Debug
        # ======================================================

        print("\nSELECTED TOOLS:")
        print(state["tools"])

        print("\nREASON:")
        print(state["reason"])

        print("\nDEEP ANALYSIS:")
        print(state["deep_analysis"])

        print("=" * 80 + "\n")

        return state

    # ==========================================================
    # JSON Cleaning
    # ==========================================================

    @staticmethod
    def _clean_json_response(
        response: str,
    ) -> str:

        response = response.strip()

        # Remove Markdown code fences.
        response = (
            response
            .replace(
                "```json",
                "",
            )
            .replace(
                "```JSON",
                "",
            )
            .replace(
                "```",
                "",
            )
            .strip()
        )

        # ------------------------------------------------------
        # If the model included extra text around the JSON,
        # extract the outermost JSON object.
        # ------------------------------------------------------

        start = response.find("{")
        end = response.rfind("}")

        if (
            start != -1
            and end != -1
            and end > start
        ):

            response = response[
                start : end + 1
            ]

        return response.strip()

    # ==========================================================
    # Planner Decision Validation
    # ==========================================================

    def _validate_decision(
        self,
        decision: Any,
    ) -> None:

        if not isinstance(
            decision,
            dict,
        ):

            raise ValueError(
                "Planner response must be a JSON object."
            )

        # ------------------------------------------------------
        # question_type
        # ------------------------------------------------------

        question_type = decision.get(
            "question_type"
        )

        if question_type is not None:

            if not isinstance(
                question_type,
                str,
            ):

                raise ValueError(
                    "Planner field 'question_type' "
                    "must be a string."
                )

        # ------------------------------------------------------
        # tools
        # ------------------------------------------------------

        tools = decision.get(
            "tools"
        )

        if tools is None:

            raise ValueError(
                "Planner response is missing 'tools'."
            )

        if not isinstance(
            tools,
            list,
        ):

            raise ValueError(
                "Planner field 'tools' "
                "must be a list."
            )

        invalid_tools = [
            tool
            for tool in tools
            if tool not in self.ALLOWED_TOOLS
        ]

        if invalid_tools:

            raise ValueError(
                "Planner selected unsupported tools: "
                f"{invalid_tools}"
            )

        # ------------------------------------------------------
        # deep_analysis
        # ------------------------------------------------------

        deep_analysis = decision.get(
            "deep_analysis"
        )

        if deep_analysis is None:

            raise ValueError(
                "Planner response is missing "
                "'deep_analysis'."
            )

        if not isinstance(
            deep_analysis,
            bool,
        ):

            raise ValueError(
                "Planner field 'deep_analysis' "
                "must be boolean."
            )

        # ------------------------------------------------------
        # reason
        # ------------------------------------------------------

        reason = decision.get(
            "reason"
        )

        if reason is not None:

            if not isinstance(
                reason,
                str,
            ):
 
                raise ValueError(
                    "Planner field 'reason' "
                    "must be a string."
                )