from __future__ import annotations


class KnowledgeResolver:
    """
    Combines knowledge returned by the different tools
    into a single context for the LLM.
    """

    def resolve(

        self,

        retrieval_context: str | None,

        graph_context: str | None,

        repository_context: str | None,

    ) -> str:

        sections = []

        # -----------------------------------------
        # Retrieval
        # -----------------------------------------

        if retrieval_context:

            sections.append(

                "========== CODE CONTEXT ==========\n"

                f"{retrieval_context}"

            )

        # -----------------------------------------
        # Graph
        # -----------------------------------------

        if graph_context:

            sections.append(

                "========== GRAPH CONTEXT ==========\n"

                f"{graph_context}"

            )

        # -----------------------------------------
        # Repository
        # -----------------------------------------

        if repository_context:

            sections.append(

                "========== REPOSITORY CONTEXT ==========\n"

                f"{repository_context}"

            )

        return "\n\n".join(sections)