from __future__ import annotations

import logging
from typing import List

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage


logger = logging.getLogger(__name__)


class LLMService:
    """
    Service responsible for communicating with the LLM.

    Responsibilities
    ----------------
    - Send messages to the LLM.
    - Return generated responses.

    This class is provider-agnostic.
    """

    def __init__(
        self,
        llm: BaseChatModel,
    ) -> None:

        self._llm = llm

    def invoke(
        self,
        messages: List[BaseMessage],
    ) -> str:

        logger.info("Invoking LLM.")

        print("\n========== LLM REQUEST ==========")

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

        print(
            f"\nTOTAL REQUEST CHARACTERS: {total_chars}"
        )

        print(
            "LLM TYPE:",
            type(self._llm).__name__,
        )

        print("=================================\n")

        response = self._llm.invoke(
            messages
        )

        return response.content