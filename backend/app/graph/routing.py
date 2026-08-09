from app.graph.state import GraphState


class Routing:

    @staticmethod
    def planner_router(state: GraphState) -> str:
        """
        Decide which node should execute next based on the
        PlannerNode output.
        """

        tools = state.get("tools", [])

        if not tools:
            return "answer"

        # Single Tool

        if len(tools) == 1:

            if tools[0] == "retrieval":
                return "retrieval"

            if tools[0] == "graph":
                return "graph"

            if tools[0] == "repository":
                return "repository"

        # Multiple tools required

        return "hybrid"