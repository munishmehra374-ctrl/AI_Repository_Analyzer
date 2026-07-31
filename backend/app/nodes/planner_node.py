import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.prompts import PLANNER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class PlannerNode:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service

    def __call__(self, state: GraphState):

        prompt = PLANNER_PROMPT.format(
            repository_uploaded=state["repository_uploaded"],
            repository_indexed=state["repository_indexed"],
            repository_name=state["repository_name"],
            primary_language=state["primary_language"],
            question=state["question"],
        )

        response = self.llm.invoke(
            [
                SystemMessage(content=prompt),
                HumanMessage(content=state["question"]),
            ]
        )

        print("\n========== PLANNER RESPONSE ==========")
        print(response)
        print(type(response))
        print("======================================\n")

        response = response.replace("```json", "").replace("```", "").strip()

        decision = json.loads(response)

        state["question_type"] = decision["question_type"]
        state["needs_retrieval"] = decision["needs_retrieval"]

        return state