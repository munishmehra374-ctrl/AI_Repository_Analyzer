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

        prompt = ANSWER_PROMPT.format(
            context=state.get("context", ""),
            question_type=state["question_type"],
        )

        print("\n========== ANSWER NODE ==========")
        print("Question:", state["question"])
        print("=================================\n")

        answer = self.llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=state["question"]),
            ]
        )

        print("\n========== FINAL ANSWER ==========")
        print(answer)
        print("==================================\n")

        state["answer"] = answer

        return state