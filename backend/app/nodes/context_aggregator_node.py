from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.core.config import get_settings
from app.graph.prompts import (
    ANALYSIS_PROMPT,
    ANSWER_PROMPT,
    SECURITY_PROMPT,
)
from app.graph.state import GraphState
from app.services.context_selection_service import (
    ContextSelectionService,
)
from app.services.llm_service import LLMService


class ContextAggregatorNode:

    def __init__(
        self,
        context_selection_service: ContextSelectionService,
        llm_service: LLMService,
    ) -> None:
        self._selector = context_selection_service
        self._llm = llm_service
        self._settings = get_settings()

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:
        print("\n========== CONTEXT AGGREGATOR ==========")

        requested_tools = state.get("tools", [])
        question = state.get("question", "")
        question_type = state.get("question_type", "general")
        deep_analysis = state.get("deep_analysis", False)

        print("Requested tools:", requested_tools)
        print("Deep analysis:", deep_analysis)

        # =====================================================
        # Candidate Contexts
        # =====================================================
        retrieval_candidates = state.get("retrieval_candidates", [])
        graph_candidates = state.get("graph_candidates", [])
        repository_candidates = state.get("repository_candidates", [])

        print("\nCandidate counts:")
        print("Retrieval:", len(retrieval_candidates))
        print("Graph:", len(graph_candidates))
        print("Repository:", len(repository_candidates))

        # =====================================================
        # Determine Context Budget
        # =====================================================
        if deep_analysis:
            next_node = "analysis -> security"

            analysis_output_reserve = (
                self._settings.ANALYSIS_MAX_OUTPUT_TOKENS
            )
            security_output_reserve = (
                self._settings.SECURITY_MAX_OUTPUT_TOKENS
            )

            analysis_prompt_without_context = ANALYSIS_PROMPT.format(
                question=question, context=""
            )
            analysis_messages = [
                SystemMessage(content=analysis_prompt_without_context),
            ]
            analysis_context_budget = self._llm.get_available_context_budget(
                analysis_messages,
                output_token_reserve=analysis_output_reserve,
            )

            security_prompt_without_context = SECURITY_PROMPT.format(
                question=question, context=""
            )
            security_messages = [
                SystemMessage(content=security_prompt_without_context),
            ]
            security_context_budget = self._llm.get_available_context_budget(
                security_messages,
                output_token_reserve=security_output_reserve,
            )

            request_token_budget = self._llm.get_request_token_budget()
            safety_margin = max(256, int(request_token_budget * 0.05))

            available_context_budget = min(
                analysis_context_budget, security_context_budget
            )
            available_context_budget = max(
                0, available_context_budget - safety_margin
            )

            limiting_agent = (
                "analysis"
                if analysis_context_budget <= security_context_budget
                else "security"
            )

            print("\n========== MULTI-AGENT BUDGET ==========")
            print("Request token budget:", self._llm.get_request_token_budget())
            print("\nAnalysis prompt context budget:", analysis_context_budget)
            print("Analysis output reservation:", analysis_output_reserve)
            print("\nSecurity prompt context budget:", security_context_budget)
            print("Security output reservation:", security_output_reserve)
            print("\nLimiting agent:", limiting_agent)
            print("Shared context budget:", available_context_budget)
            print("========================================\n")

            output_token_reserve = self._settings.SECURITY_MAX_OUTPUT_TOKENS

        else:
            next_node = "answer"
            output_token_reserve = self._settings.ANSWER_MAX_OUTPUT_TOKENS

            prompt_without_context = ANSWER_PROMPT.format(
                context="", question_type=question_type
            )
            messages_without_context = [
                SystemMessage(content=prompt_without_context),
                HumanMessage(content=question),
            ]
            available_context_budget = self._llm.get_available_context_budget(
                messages_without_context,
                output_token_reserve=output_token_reserve,
            )

            print("\n========== ANSWER BUDGET DEBUG ==========")
            print(
                "Prompt WITHOUT context tokens:",
                self._llm._token_counter(messages_without_context),
            )
            print(
                "Output reservation:",
                output_token_reserve,
            )
            print(
                "Available context budget:",
                available_context_budget,
            )
            print("=========================================\n")

        state["available_context_budget"] = available_context_budget
        state["context_output_reserve"] = output_token_reserve

        # =====================================================
        # Preserve Retrieval Source Metadata (Safely)
        # =====================================================
        enriched_retrieval_candidates = []

        for candidate in retrieval_candidates:
            if isinstance(candidate, dict):
                candidate_copy = dict(candidate)
                code = candidate_copy.get("code", "")
                file_path = candidate_copy.get("file_path", "")
                name = candidate_copy.get("name", "")
                qualified_name = candidate_copy.get("qualified_name", "")
                start_line = candidate_copy.get("start_line", "")
                end_line = candidate_copy.get("end_line", "")

                source_metadata = (
                    "\n\n"
                    "===== RETRIEVAL SOURCE =====\n"
                    f"File: {file_path}\n"
                    f"Name: {name}\n"
                    f"Qualified Name: {qualified_name}\n"
                    f"Lines: {start_line}-{end_line}\n"
                    "===== CODE =====\n"
                )
                candidate_copy["content"] = source_metadata + str(code)
                enriched_retrieval_candidates.append(candidate_copy)
            else:
                enriched_retrieval_candidates.append(candidate)

        # =====================================================
        # GLOBAL CONTEXT SELECTION
        # =====================================================
        final_context = self._selector.select_context(
            question=question,
            retrieval_candidates=enriched_retrieval_candidates,
            graph_candidates=graph_candidates,
            repository_candidates=repository_candidates,
            available_context_budget=available_context_budget,
            requested_tools=requested_tools,
            deep_analysis=deep_analysis,
        )

        print("\n========== SELECTED FINAL CONTEXT ==========")
        print(final_context)
        print("=============================================\n")


        state["context"] = final_context

        return state