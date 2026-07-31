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
        """
        Invoke the language model.

        Parameters
        ----------
        messages:
            Conversation messages.

        Returns
        -------
        str
            Generated response.
        """

        logger.info("Invoking LLM.")

        response = self._llm.invoke(messages)

        return response.content