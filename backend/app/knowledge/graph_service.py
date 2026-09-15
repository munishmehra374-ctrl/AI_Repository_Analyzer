from app.knowledge.graph_builder import GraphBuilder
from app.knowledge.neo4j_store import Neo4jStore


class GraphService:

    # Incremental indexing test

    def __init__(self):

        self.builder = GraphBuilder()
        self.neo4j = Neo4jStore()

    def build_graph(
        self,
        extracted_files: list[dict],
        repository_id: str,
        changed_files: list[str] | None = None,
    ):

        print(
            "\n========== GRAPH SERVICE BUILD_GRAPH =========="
        )

        print(
            "Repository ID:",
            repository_id,
        )

        print(
            "Extracted files:",
            len(extracted_files),
        )

        print(
            "Changed files:",
            len(changed_files or []),
        )

        print(
            "===============================================\n"
        )

        # -------------------------------------------------
        # Keep the existing graph-building logic.
        #
        # IMPORTANT:
        # GraphBuilder still receives ALL extracted files
        # so cross-file relationships continue to resolve.
        # -------------------------------------------------

        graph = self.builder.build_repository(
            extracted_files
        )

        # -------------------------------------------------
        # Store graph
        #
        # First indexing:
        #     full graph storage
        #
        # Incremental indexing:
        #     only changed-file graph data is updated
        # -------------------------------------------------

        if changed_files:

            self.neo4j.update_graph(
                graph=graph,
                repository_id=repository_id,
                changed_files=changed_files,
            )

        else:

            self.neo4j.store_graph(
                graph,
                repository_id,
            )

        return graph