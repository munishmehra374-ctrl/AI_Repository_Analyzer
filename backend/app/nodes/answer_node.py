from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.prompts import ANSWER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class AnswerNode:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm = llm_service

    def __call__(
        self,
        state: GraphState,
    ):

        context = state.get("context") or ""

        question_type = state.get(
            "question_type",
            "general",
        )

        prompt = ANSWER_PROMPT.format(
            context=context,
            question_type=question_type,
        )

        print("\n========== ANSWER NODE ==========")
        print("Question:", state["question"])
        print("Question Type:", question_type)
        print("=================================\n")

        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=state["question"]),
        ]

        answer = self.llm.invoke(
            messages
        )

        print("\n========== FINAL ANSWER ==========")
        print(answer)
        print("==================================\n")

        state["answer"] = answer

        return state