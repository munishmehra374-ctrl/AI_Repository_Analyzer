import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.graph.prompts import PLANNER_PROMPT
from app.graph.state import GraphState
from app.services.llm_service import LLMService


class PlannerNode:

    def __init__(
        self,
        llm_service: LLMService,
    ):
        self.llm = llm_service

    def __call__(
        self,
        state: GraphState,
    ):

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

        print("\n========== PLANNER RAW RESPONSE ==========")
        print(response)
        print("==========================================\n")

        response = (
            response.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        print("\n========== CLEANED RESPONSE ==========")
        print(response)
        print("======================================\n")

        try:
            decision = json.loads(response)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Planner returned invalid JSON:\n{response}"
            ) from e

        print("\n========== PLANNER DECISION ==========")
        print(decision)
        print("======================================\n")

        state["question_type"] = decision.get(
            "question_type",
            "repository",
        )

        state["tools"] = decision.get(
            "tools",
            [],
        )

        state["reason"] = decision.get(
            "reason",
            "",
        )

        print("\n========== STATE AFTER PLANNER ==========")
        print("Question Type :", state["question_type"])
        print("Tools         :", state["tools"])
        print("Reason        :", state["reason"])
        print("=========================================\n")

        return state