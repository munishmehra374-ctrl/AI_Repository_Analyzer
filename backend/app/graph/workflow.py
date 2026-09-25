from langgraph.graph import StateGraph, START, END

from app.graph.dependencies import dependencies
from app.graph.state import GraphState

from app.nodes.planner_node import PlannerNode
from app.nodes.tool_executor_node import ToolExecutorNode
from app.nodes.context_aggregator_node import ContextAggregatorNode
from app.nodes.analysis_node import AnalysisNode
from app.nodes.root_cause_node import RootCauseNode
from app.nodes.reviewer_node import ReviewerNode
from app.nodes.answer_node import AnswerNode
from app.nodes.title_node import TitleNode


def create_workflow(
    repository_id: str,
):

    # =========================================================
    # Repository-specific tools
    # =========================================================

    retrieval_tool = dependencies.get_retrieval_tool(
        repository_id
    )

    if retrieval_tool is None:

        raise ValueError(
            f"No retrieval tool found for repository: "
            f"{repository_id}"
        )

    graph_tool = dependencies.get_graph_tool(
        repository_id
    )

    if graph_tool is None:

        raise ValueError(
            f"No graph tool found for repository: "
            f"{repository_id}"
        )

    # =========================================================
    # Planner
    # =========================================================

    planner = PlannerNode(
        dependencies.llm_service,
        entity_resolver=getattr(graph_tool, "entity_resolver", None),
    )

    # =========================================================
    # Tool Executor
    # =========================================================

    tool_executor = ToolExecutorNode(
        retrieval_tool,
        graph_tool,
        dependencies.repository_tool,
    )

    print(
        "\n========== WORKFLOW TOOL DEBUG =========="
    )

    print(
        "retrieval_tool:",
        retrieval_tool,
    )

    print(
        "retrieval_tool class:",
        retrieval_tool.__class__,
    )

    print(
        "retrieval_tool module:",
        retrieval_tool.__class__.__module__,
    )

    print(
        "retrieval_tool execute:",
        getattr(
            retrieval_tool,
            "execute",
            None,
        ),
    )

    print(
        "graph_tool:",
        graph_tool,
    )

    print(
        "graph_tool class:",
        graph_tool.__class__,
    )

    print(
        "graph_tool module:",
        graph_tool.__class__.__module__,
    )

    print(
        "=========================================\n"
    )

    # =========================================================
    # Context Aggregator
    # =========================================================

    context_aggregator = ContextAggregatorNode(
        dependencies.context_selection_service,
        dependencies.llm_service,
    )

    # =========================================================
    # Analysis
    # =========================================================

    analysis = AnalysisNode(
        dependencies.llm_service
    )

    # =========================================================
    # Root Cause / Security Architecture
    # =========================================================

    security_architecture = RootCauseNode(
        dependencies.llm_service
    )

    # =========================================================
    # Reviewer
    # =========================================================

    reviewer = ReviewerNode(
        dependencies.llm_service
    )

    # =========================================================
    # Answer
    # =========================================================

    answer = AnswerNode(
        dependencies.llm_service
    )

    title = TitleNode(
        dependencies.llm_service
    )

    workflow = StateGraph(GraphState)

    # =========================================================
    # Nodes
    # =========================================================

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
        "analysis",
        analysis,
    )

    workflow.add_node(
        "security_architecture",
        security_architecture,
    )

    workflow.add_node(
        "reviewer",
        reviewer,
    )

    workflow.add_node(
        "answer",
        answer,
    )

    workflow.add_node(
    "title",
    title,
    )

    # =========================================================
    # Initial Pipeline
    # =========================================================

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

    # =========================================================
    # Conditional Routing After Context Aggregation
    # =========================================================

    def route_after_context(
        state: GraphState,
    ):

        if state.get(
            "deep_analysis",
            False,
        ):

            return [
                "analysis",
                "security_architecture",
            ]

        return "answer"

    workflow.add_conditional_edges(
        "context_aggregator",
        route_after_context,
        {
            "analysis": "analysis",
            "security_architecture": (
                "security_architecture"
            ),
            "answer": "answer",
        },
    )

    # =========================================================
    # Parallel Multi-Agent Pipeline
    # =========================================================

    workflow.add_edge(
        "analysis",
        "reviewer",
    )

    workflow.add_edge(
        "security_architecture",
        "reviewer",
    )

    # =========================================================
    # Reviewer → Final Answer
    # =========================================================

    workflow.add_edge(
        "reviewer",
        "answer",
    )

    # =========================================================
    # Final Answer → END
    # =========================================================

    workflow.add_edge(
        "answer",
        "title",
    )

    workflow.add_edge(
        "title",
        END,
    )

    return workflow.compile()