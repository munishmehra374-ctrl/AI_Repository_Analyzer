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
                repository_context = str(
                    repository_context
                )

            repository_context = (
                repository_context.strip()
            )

            if (
                repository_context
                and repository_context not in seen
            ):

                seen.add(repository_context)

                context_sections.append(
                    """
====================================================
REPOSITORY CONTEXT
====================================================

This context contains repository-level information
such as project structure, technologies, services,
frameworks and repository metadata.

"""
                    + repository_context
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
                graph_context = str(
                    graph_context
                )

            graph_context = (
                graph_context.strip()
            )

            if (
                graph_context
                and graph_context not in seen
            ):

                seen.add(graph_context)

                context_sections.append(
                    """
====================================================
KNOWLEDGE GRAPH CONTEXT
====================================================

This context contains structural relationships
between repository entities such as functions,
classes, dependencies, inheritance and imports.

"""
                    + graph_context
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
                retrieval_context = str(
                    retrieval_context
                )

            retrieval_context = (
                retrieval_context.strip()
            )

            if (
                retrieval_context
                and retrieval_context not in seen
            ):

                seen.add(retrieval_context)

                context_sections.append(
                    """
====================================================
CODE RETRIEVAL CONTEXT
====================================================

This context contains code retrieved from the
repository using semantic and keyword search.

"""
                    + retrieval_context
                )

        # =====================================================
        # Final Context
        # =====================================================

        if context_sections:

            state["context"] = "\n\n".join(
                context_sections
            )

        else:

            state["context"] = (
                "No repository context was found."
            )

        print("\n========== FINAL CONTEXT ==========")
        print(state["context"])
        print("===================================\n")

        return state