from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.graph.state import GraphState
from app.services.llm_service import LLMService


TITLE_PROMPT = """
Generate a short, clear title for this conversation.

Rules:
- Maximum 6 words.
- Return ONLY the title.
- Do not use quotation marks.
- Do not add explanations.
- The title should describe the user's question.

User question:
"""


class TitleNode:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm = llm_service

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        print("\n========== TITLE NODE ==========")
        print("generate_title:", state.get("generate_title"))
        print("question:", state.get("question"))
        print("================================\n")


        # Only generate a title when requested.
        if not state.get(
            "generate_title",
            False,
        ):
            return state

        question = state.get(
            "question",
            "",
        ).strip()

        if not question:
            return state

        messages = [
            SystemMessage(
                content=TITLE_PROMPT
            ),
            HumanMessage(
                content=question
            ),
        ]

        title = self.llm.invoke(
            messages,
            max_output_tokens=300,
        )

        print("\n========== TITLE LLM RESULT ==========")
        print("RAW TITLE:", repr(title))
        print("======================================\n")

        title = title.strip()

        # Remove accidental quotation marks.
        title = title.strip("\"'")

        state["title"] = title

        print("\n========== TITLE STATE ==========")
        print("FINAL TITLE:", repr(state["title"]))
        print("=================================\n")

        return state