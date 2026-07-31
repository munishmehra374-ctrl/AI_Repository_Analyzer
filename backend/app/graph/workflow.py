from langgraph.graph import StateGraph, START, END

from app.graph.state import GraphState
from app.graph.dependencies import dependencies

from app.nodes.planner_node import PlannerNode
from app.nodes.retrieval_node import RetrievalNode
from app.nodes.answer_node import AnswerNode


def create_workflow():

    planner = PlannerNode(
        dependencies.llm_service
    )

    retrieval = RetrievalNode(
        dependencies.retrieval_service
    )

    answer = AnswerNode(
        dependencies.llm_service
    )

    workflow = StateGraph(GraphState)

    workflow.add_node("planner", planner)
    workflow.add_node("retrieval", retrieval)
    workflow.add_node("answer", answer)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "retrieval")
    workflow.add_edge("retrieval", "answer")
    workflow.add_edge("answer", END)

    return workflow.compile()