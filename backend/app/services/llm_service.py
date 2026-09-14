from __future__ import annotations

import logging
from typing import Callable, List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage


logger = logging.getLogger(__name__)


class LLMService:
    """
    Provider-agnostic service responsible for communicating
    with the configured LLM.

    Responsibilities:

    1. Count request tokens.
    2. Validate the application-level request budget.
    3. Calculate available context budget.
    4. Apply a per-agent output-token limit.
    5. Provide detailed token usage diagnostics.

    The service does NOT assume a specific LLM provider.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        request_token_budget: int,
        token_counter: Callable[[List[BaseMessage]], int],
        output_token_reserve: int,
    ) -> None:

        if request_token_budget <= 0:
            raise ValueError(
                "request_token_budget must be greater than zero."
            )

        if output_token_reserve <= 0:
            raise ValueError(
                "output_token_reserve must be greater than zero."
            )

        if not callable(token_counter):
            raise TypeError(
                "token_counter must be callable."
            )

        self._llm = llm

        self._request_token_budget = (
            request_token_budget
        )

        self._token_counter = token_counter

        # Used when calculating repository context.
        self._output_token_reserve = (
            output_token_reserve
        )


    # ==========================================================
    # Public Token Utilities
    # ==========================================================

    def count_messages(
        self,
        messages: List[BaseMessage],
    ) -> int:
        """
        Count tokens using the same tokenizer used to
        validate actual LLM requests.
        """

        return self._token_counter(messages)

    def get_request_token_budget(self) -> int:
        """
        Return the maximum input-token budget allowed
        for a single LLM request.
        """

        return self._request_token_budget

    # ==========================================================
    # Context Budget
    # ==========================================================

    def get_available_context_budget(
        self,
        messages_without_context: List[BaseMessage],
        output_token_reserve: Optional[int] = None,
    ) -> int:
        """
        Calculate how many tokens are available for repository
        context.

        Final request:

            prompt/question
            + repository context
            + output reservation

        Therefore:

            context budget =
                request budget
                - prompt/question tokens
                - output reservation

        A different output reservation can optionally be supplied
        for agents with different output requirements.
        """

        prompt_tokens = self._token_counter(
            messages_without_context
        )

        reserve = (
            output_token_reserve
            if output_token_reserve is not None
            else self._output_token_reserve
        )

        if reserve <= 0:
            raise ValueError(
                "output_token_reserve must be greater than zero."
            )

        available_context_budget = (
            self._request_token_budget
            - prompt_tokens
            - reserve
        )

        print(
            "\n========== CONTEXT BUDGET CALCULATION =========="
        )

        print(
            "Request token budget:",
            self._request_token_budget,
        )

        print(
            "Prompt/question tokens:",
            prompt_tokens,
        )

        print(
            "Output token reservation:",
            reserve,
        )

        print(
            "Available context tokens:",
            available_context_budget,
        )

        print(
            "================================================\n"
        )

        return max(
            0,
            available_context_budget,
        )

    # ==========================================================
    # LLM Invocation
    # ==========================================================

    def invoke(
        self,
        messages: List[BaseMessage],
        max_output_tokens: Optional[int] = None,
    ) -> str:
        """
        Invoke the configured LLM.

        max_output_tokens:

            Optional maximum number of tokens that this particular
            agent is allowed to generate.

        Example:

            planner:
                max_output_tokens=512

            analysis:
                max_output_tokens=1200

            security:
                max_output_tokens=1200

            reviewer:
                max_output_tokens=800

            answer:
                max_output_tokens=1000
        """

        logger.info(
            "Invoking LLM."
        )

        # ======================================================
        # Determine output limit
        # ======================================================

        effective_output_limit = (
            max_output_tokens
            if max_output_tokens is not None
            else self._output_token_reserve
        )

        if effective_output_limit <= 0:
            raise ValueError(
                "max_output_tokens must be greater than zero."
            )

        # ======================================================
        # Debug request
        # ======================================================

        print(
            "\n========== LLM REQUEST =========="
        )

        total_chars = 0

        for message in messages:

            content = message.content

            print(
                f"\nMessage type: {type(message).__name__}"
            )

            print(
                f"Characters: {len(content)}"
            )

            total_chars += len(content)

        # ======================================================
        # Count input/request tokens
        # ======================================================

        request_tokens = self._token_counter(
            messages
        )

        remaining_request_budget = (
            self._request_token_budget
            - request_tokens
        )

        print(
            "\nREQUEST TOKENS:",
            request_tokens,
        )

        print(
            "REQUEST TOKEN BUDGET:",
            self._request_token_budget,
        )

        print(
            "PER-AGENT MAX OUTPUT TOKENS:",
            effective_output_limit,
        )

        print(
            "REMAINING REQUEST TOKEN BUDGET:",
            remaining_request_budget,
        )

        print(
            "TOTAL REQUEST CHARACTERS:",
            total_chars,
        )

        print(
            "LLM TYPE:",
            type(self._llm).__name__,
        )

        print(
            "=================================\n"
        )

        # ======================================================
        # Validate request
        # ======================================================

        if request_tokens > self._request_token_budget:

            raise ValueError(
                "LLM request exceeds the configured token budget. "
                f"Requested input tokens: {request_tokens}, "
                f"Budget: {self._request_token_budget}."
            )

        # ======================================================
        # Validate output against remaining request budget
        # ======================================================

        if effective_output_limit > remaining_request_budget:

            print(
                "\nWARNING:"
            )

            print(
                "Requested output limit is larger than the "
                "remaining application request budget."
            )

            print(
                "Requested output:",
                effective_output_limit,
            )

            print(
                "Remaining budget:",
                remaining_request_budget,
            )

            print(
                "Using remaining budget as effective output limit."
            )

            effective_output_limit = max(
                1,
                remaining_request_budget,
            )

        # ======================================================
        # Ensure at least one HumanMessage for chat template compatibility
        # ======================================================

        from langchain_core.messages import HumanMessage

        has_user_message = any(
            isinstance(m, HumanMessage)
            or getattr(m, "type", "") in ("human", "user")
            for m in messages
        )

        call_messages = (
            list(messages)
            if has_user_message
            else list(messages) + [HumanMessage(content="Please proceed.")]
        )

        # ======================================================
        # Call LLM
        # ======================================================

        response = self._llm.invoke(
            call_messages,
            max_tokens=effective_output_limit,
        )

        # ======================================================
        # Debug LLM response
        # ======================================================

        print(
            "\n========== RAW LLM RESPONSE =========="
        )

        print(
            "Response type:",
            type(response),
        )

        print(
            "Response content:",
            repr(
                response.content
            ),
        )

        print(
            "Content type:",
            type(response.content),
        )

        if hasattr(
            response,
            "response_metadata",
        ):

            print(
                "Response metadata:",
                response.response_metadata,
            )

        if hasattr(
            response,
            "usage_metadata",
        ):

            print(
                "Usage metadata:",
                response.usage_metadata,
            )

        print(
            "======================================\n"
        )

        return response.content