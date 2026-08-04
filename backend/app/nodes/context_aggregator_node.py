from app.graph.state import GraphState


class ContextAggregatorNode:

    def __call__(
        self,
        state: GraphState,
    ) -> GraphState:

        print("\n========== CONTEXT AGGREGATOR ==========")

        context_sections = []

        seen = set()
        # =====================================================
        # Repository Context
        # =====================================================

        repository_context = state.get(
            "repository_context"
        )

        print("\nRepository Context:")
        print(repository_context)

        if repository_context:

            if not isinstance(repository_context, str):
                repository_context = str(repository_context)

            if (
                repository_context.strip()
                and repository_context not in seen
            ):

                seen.add(repository_context)

                context_sections.append(
                    "========== REPOSITORY CONTEXT ==========\n"
                    f"{repository_context}"
                )
                
        # =====================================================
        # Graph Context
        # =====================================================

        graph_context = state.get(
            "graph_context"
        )

        print("\nGraph Context:")
        print(graph_context)

        if graph_context:

            if not isinstance(graph_context, str):
                graph_context = str(graph_context)

            if (
                graph_context.strip()
                and graph_context not in seen
            ):

                seen.add(graph_context)

                context_sections.append(
                    "========== GRAPH CONTEXT ==========\n"
                    f"{graph_context}"
                )

        # =====================================================
        # Retrieval Context
        # =====================================================

        retrieval_context = state.get(
            "retrieval_context"
        )

        print("\nRetrieval Context:")
        print(retrieval_context)

        if retrieval_context:

            if not isinstance(retrieval_context, str):
                retrieval_context = str(retrieval_context)

            if (
                retrieval_context.strip()
                and retrieval_context not in seen
            ):

                seen.add(retrieval_context)

                context_sections.append(
                    "========== CODE CONTEXT ==========\n"
                    f"{retrieval_context}"
                )

        # =====================================================
        # Final Context
        # =====================================================

        state["context"] = "\n\n".join(
            context_sections
        )

        print("\n========== FINAL CONTEXT ==========")
        print(state["context"])
        print("===================================\n")

        return state