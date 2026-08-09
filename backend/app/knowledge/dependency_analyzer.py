from __future__ import annotations

from app.knowledge.models import (
    RepositoryGraph,
    Relationship,
)


class DependencyAnalyzer:
    """
    Builds dependency relationships between classes.

    Example
    -------

    self.chunk_service = ChunkService()

    becomes

    IndexingService
          |
      DEPENDS_ON
          |
      ChunkService
    """

    def analyze(
        self,
        graph: RepositoryGraph,
    ) -> RepositoryGraph:

        for function in graph.functions.values():

            # Only constructor injection
            if function.name != "__init__":
                continue

            if function.class_name is None:
                continue

            for dependency in function.dependencies:

                dependency_class = dependency.get(
                    "class"
                )

                if not dependency_class:
                    continue

                graph.relationships.append(

                    Relationship(

                        source=function.class_name,

                        target=dependency_class,

                        relationship_type="DEPENDS_ON",
                    )

                )

        return graph