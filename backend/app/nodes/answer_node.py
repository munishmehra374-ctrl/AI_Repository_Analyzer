from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.prompts import ANSWER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class AnswerNode:

    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def __call__(self, state: GraphState):

        prompt = ANSWER_PROMPT.format(
            context=state["context"],
            question=state["question"]
        )

        response = self.llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=state["question"]),
            ]
        )

        state["answer"] = response

        return state