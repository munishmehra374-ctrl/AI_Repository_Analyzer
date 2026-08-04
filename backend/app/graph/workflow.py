from langgraph.graph import StateGraph, START, END

from app.graph.dependencies import dependencies
from app.graph.state import GraphState

from app.nodes.planner_node import PlannerNode
from app.nodes.tool_executor_node import ToolExecutorNode
from app.nodes.context_aggregator_node import ContextAggregatorNode
from app.nodes.answer_node import AnswerNode


def create_workflow():

    planner = PlannerNode(
        dependencies.llm_service
    )

    tool_executor = ToolExecutorNode(
        dependencies.retrieval_tool,
        dependencies.graph_tool,
        dependencies.repository_tool,
    )

    context_aggregator = ContextAggregatorNode()

    answer = AnswerNode(
        dependencies.llm_service
    )

    workflow = StateGraph(GraphState)

    workflow.add_node(
        "planner",
        planner,
    )

    workflow.add_node(
        "tool_executor",
        tool_executor,
    )

    workflow.add_node(
        "context_aggregator",
        context_aggregator,
    )

    workflow.add_node(
        "answer",
        answer,
    )

    workflow.add_edge(
        START,
        "planner",
    )

    workflow.add_edge(
        "planner",
        "tool_executor",
    )

    workflow.add_edge(
        "tool_executor",
        "context_aggregator",
    )

    workflow.add_edge(
        "context_aggregator",
        "answer",
    )

    workflow.add_edge(
        "answer",
        END,
    )

    return workflow.compile()