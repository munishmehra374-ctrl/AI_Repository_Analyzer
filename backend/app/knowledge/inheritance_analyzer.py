from __future__ import annotations

from app.knowledge.models import (
    RepositoryGraph,
    Relationship,
)


class InheritanceAnalyzer:
    """
    Creates INHERITS relationships.

    Example
    -------

    class HybridRetriever(BaseRetriever)

    becomes

    HybridRetriever

            |

        INHERITS

            |

    BaseRetriever
    """

    def analyze(
        self,
        graph: RepositoryGraph,
    ) -> RepositoryGraph:

        for cls in graph.classes.values():

            if not cls.base_classes:

                continue

            for parent in cls.base_classes:

                graph.relationships.append(

                    Relationship(

                        source=cls.name,

                        target=parent,

                        relationship_type="INHERITS",

                    )

                )

        return graph