from __future__ import annotations

import re

from app.knowledge.models import (
    RepositoryGraph,
    Relationship,
)


class ImportAnalyzer:
    """
    Converts Python import statements into
    IMPORTS relationships.

    Example
    -------

    from app.services.graph_service import GraphService

    becomes

    current_file.py
        |
    IMPORTS
        |
    app.services.graph_service
    """

    def analyze(
        self,
        graph: RepositoryGraph,
    ) -> RepositoryGraph:

        for file in graph.files.values():

            imports = self._get_imports(
                graph,
                file.path,
            )

            for module in imports:

                graph.relationships.append(

                    Relationship(

                        source=file.path,

                        target=module,

                        relationship_type="IMPORTS",

                    )

                )

        return graph

    # =====================================================
    # Extract imports belonging to a file
    # =====================================================

    def _get_imports(
        self,
        graph: RepositoryGraph,
        file_path: str,
    ) -> list[str]:

        modules = []

        for import_node in graph.imports.values():

            statement = import_node.statement

            # ------------------------------------------
            # import os
            # import numpy as np
            # ------------------------------------------

            match = re.match(
                r"import\s+([A-Za-z0-9_\.]+)",
                statement,
            )

            if match:

                modules.append(
                    match.group(1)
                )

                continue

            # ------------------------------------------
            # from app.services.graph_service
            # import GraphService
            # ------------------------------------------

            match = re.match(
                r"from\s+([A-Za-z0-9_\.]+)\s+import",
                statement,
            )

            if match:

                modules.append(
                    match.group(1)
                )

        return modules