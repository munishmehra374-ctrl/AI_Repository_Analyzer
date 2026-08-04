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

        print("\n========== TOOL EXECUTOR ==========")
        print("Question:", question)
        print("Requested Tools:", requested_tools)
        print("===================================\n")

        # Reset contexts
        state["retrieval_context"] = None
        state["graph_context"] = None
        state["repository_context"] = None

        if not requested_tools:

            print("No tools selected by Planner.\n")
            return state

        for tool_name in requested_tools:

            tool = self.tools.get(tool_name)

            if tool is None:

                print(f"Unknown tool: {tool_name}")
                continue

            executor, context_key = tool

            print(f"\n---------- Running {tool_name} ----------")

            result = executor.execute(question)

            print(f"{tool_name} returned:")
            print(result)

            state[context_key] = result

            print(f"Stored in state['{context_key}']")
            print("----------------------------------------\n")

        print("\n========== TOOL EXECUTOR COMPLETE ==========")
        print("retrieval_context :", state["retrieval_context"])
        print("graph_context     :", state["graph_context"])
        print("repository_context:", state["repository_context"])
        print("============================================\n")

        return state