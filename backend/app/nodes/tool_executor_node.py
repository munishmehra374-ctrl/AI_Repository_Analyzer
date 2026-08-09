from app.graph.state import GraphState

from app.tools.retrieval_tool import RetrievalTool
from app.tools.graph_tool import GraphTool
from app.tools.repository_tool import RepositoryTool


class ToolExecutorNode:

    def __init__(
        self,
        retrieval_tool: RetrievalTool,
        graph_tool: GraphTool,
        repository_tool: RepositoryTool,
    ):
        self.tools = {
            "retrieval": (
                retrieval_tool,
                "retrieval_context",
            ),
            "graph": (
                graph_tool,
                "graph_context",
            ),
            "repository": (
                repository_tool,
                "repository_context",
            ),
        }

    def __call__(
        self,
        state: GraphState,
    ):

        question = state["question"]

        requested_tools = state.get(
            "tools",
            [],
        )

        print("\n" + "=" * 80)
        print("TOOL EXECUTOR")
        print("=" * 80)
        print("Question:", question)
        print("Requested Tools:", requested_tools)

        # Reset contexts
        state["retrieval_context"] = None
        state["graph_context"] = None
        state["repository_context"] = None

        if not requested_tools:

            print("Planner selected NO tools.")
            print("=" * 80 + "\n")
            return state

        for tool_name in requested_tools:

            print(f"\nRunning Tool: {tool_name}")

            tool = self.tools.get(tool_name)

            if tool is None:
                print(f"Unknown tool: {tool_name}")
                continue

            executor, context_key = tool

            result = executor.execute(question)

            print(f"\nResult from {tool_name}:")
            print(result)

            state[context_key] = result

            print(f"\nStored in state['{context_key}']")

        print("\n" + "=" * 80)
        print("FINAL TOOL CONTEXTS")
        print("=" * 80)

        print("\nRetrieval Context:")
        print(state["retrieval_context"])

        print("\nGraph Context:")
        print(state["graph_context"])

        print("\nRepository Context:")
        print(state["repository_context"])

        print("=" * 80 + "\n")

        return state