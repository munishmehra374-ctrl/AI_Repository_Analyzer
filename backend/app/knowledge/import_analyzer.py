from __future__ import annotations

import os
import re

from app.knowledge.models import (
    RepositoryGraph,
    Relationship,
)


class ImportAnalyzer:
    """
    Converts Python import statements into
    IMPORTS relationships between File nodes.

    Example
    -------

    from app.knowledge.graph_service import GraphService

    becomes:

    indexing_service.py
        |
      IMPORTS
        |
    graph_service.py
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

                target_file = self._resolve_module_to_file(
                    graph,
                    module,
                )

                if target_file is None:
                    continue

                # Avoid duplicate relationships
                already_exists = any(
                    relationship.source == file.path
                    and relationship.target == target_file
                    and relationship.relationship_type == "IMPORTS"
                    for relationship in graph.relationships
                )

                if already_exists:
                    continue

                graph.relationships.append(
                    Relationship(
                        source=file.path,
                        target=target_file,
                        relationship_type="IMPORTS",
                    )
                )

                print(
                    "FILE IMPORT RELATIONSHIP:",
                    file.path,
                    "->",
                    target_file,
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

            # IMPORTANT:
            # Only use imports belonging to this file.
            if import_node.file_path != file_path:
                continue

            statement = import_node.statement

            # ------------------------------------------
            # import app.knowledge.graph_service
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
            # from app.knowledge.graph_service
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

    # =====================================================
    # Resolve Python module -> actual repository file
    # =====================================================

    def _resolve_module_to_file(
        self,
        graph: RepositoryGraph,
        module: str,
    ) -> str | None:

        # ------------------------------------------
        # app.knowledge.graph_service
        #
        # becomes:
        #
        # app/knowledge/graph_service.py
        # ------------------------------------------

        module_path = module.replace(
            ".",
            os.sep,
        )

        expected_path = (
            module_path
            + ".py"
        )

        # Normalize separators so this works
        # with Windows paths as well.
        expected_path = expected_path.replace(
            "\\",
            "/",
        ).lower()

        for file in graph.files.values():

            actual_path = file.path.replace(
                "\\",
                "/",
            ).lower()

            if actual_path.endswith(
                "/" + expected_path
            ):

                return file.path

        return None