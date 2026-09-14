from __future__ import annotations

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory responsible for creating chat models.

    This is the ONLY place where provider-specific
    chat models are instantiated.
    """

    @staticmethod
    def create() -> BaseChatModel:

        settings = get_settings()

        logger.info(
            "Initializing LLM provider: %s",
            settings.LLM_PROVIDER,
        )

        if settings.LLM_PROVIDER.lower() == "groq":

            return ChatGroq(
                model=settings.GROQ_MODEL,
                api_key=settings.GROQ_API_KEY,
                temperature=settings.TEMPERATURE,
                max_tokens=settings.OUTPUT_TOKEN_RESERVE,
            )

        raise ValueError(
            f"Unsupported LLM provider: {settings.LLM_PROVIDER}"
        )