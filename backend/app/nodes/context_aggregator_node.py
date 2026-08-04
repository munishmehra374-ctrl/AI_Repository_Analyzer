from app.graph.state import GraphState


class ContextAggregatorNode:

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        contexts = []

        print("\n========== CONTEXT AGGREGATOR ==========")

        # -----------------------------------
        # Retrieval Context
        # -----------------------------------

        retrieval_context = state.get(
            "retrieval_context"
        )

        print("\nRetrieval Context:")
        print(retrieval_context)

        if retrieval_context:

            contexts.append(
                "========== CODE CONTEXT ==========\n"
                f"{retrieval_context}"
            )

        # -----------------------------------
        # Graph Context
        # -----------------------------------

        graph_context = state.get(
            "graph_context"
        )

        print("\nGraph Context:")
        print(graph_context)

        if graph_context:

            contexts.append(
                "========== GRAPH CONTEXT ==========\n"
                f"{graph_context}"
            )

        # -----------------------------------
        # Repository Context
        # -----------------------------------

        repository_context = state.get(
            "repository_context"
        )

        print("\nRepository Context:")
        print(repository_context)

        if repository_context:

            contexts.append(
                "========== REPOSITORY CONTEXT ==========\n"
                f"{repository_context}"
            )

        # -----------------------------------
        # Final Context
        # -----------------------------------

        state["context"] = "\n\n".join(
            contexts
        )

        print("\n========== FINAL CONTEXT ==========")
        print(state["context"])
        print("===================================\n")

        return state