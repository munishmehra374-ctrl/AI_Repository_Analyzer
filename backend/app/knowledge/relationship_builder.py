from __future__ import annotations

import os

from app.knowledge.models import (
    RepositoryGraph,
    Relationship,
)


class RelationshipBuilder:
    """
    Builds structural relationships for the RepositoryGraph.

    Responsibilities
    ----------------
    - Repository -> Folder
    - Folder -> File
    - File -> Import
    - File -> Class
    - File -> Function
    - Class -> Method
    - Function -> Function (CALLS)
    - Class -> Parent Class (INHERITS)
    """

    def build(
        self,
        graph: RepositoryGraph,
    ) -> RepositoryGraph:

        self._repository_relationships(graph)

        self._file_relationships(graph)

        self._import_relationships(graph)

        self._class_relationships(graph)

        self._function_relationships(graph)

        self._inheritance_relationships(graph)

        return graph
    # =====================================================
    # Repository -> Folder
    # =====================================================

    def _repository_relationships(
        self,
        graph: RepositoryGraph,
    ):

        if graph.repository is None:
            return

        for folder in graph.folders.values():

            graph.relationships.append(
                Relationship(
                    source=graph.repository.path,
                    target=folder.path,
                    relationship_type="HAS_FOLDER",
                )
            )

    # =====================================================
    # Folder -> File
    # =====================================================

    def _file_relationships(
        self,
        graph: RepositoryGraph,
    ):

        for file in graph.files.values():

            folder = os.path.dirname(file.path)

            if folder:

                graph.relationships.append(
                    Relationship(
                        source=folder,
                        target=file.path,
                        relationship_type="HAS_FILE",
                    )
                )

    # =====================================================
    # File -> Import
    # =====================================================

    def _import_relationships(
        self,
        graph: RepositoryGraph,
    ):

        if not graph.files:
            return

        file = next(iter(graph.files.values()))

        for imp in graph.imports.values():

            graph.relationships.append(
                Relationship(
                    source=file.path,
                    target=imp.statement,
                    relationship_type="IMPORTS",
                )
            )

    # =====================================================
    # File -> Class
    # =====================================================

    def _class_relationships(
        self,
        graph: RepositoryGraph,
    ):

        for cls in graph.classes.values():

            graph.relationships.append(
                Relationship(
                    source=cls.file_path,
                    target=cls.name,
                    relationship_type="HAS_CLASS",
                )
            )

    # =====================================================
    # File -> Function
    # =====================================================

    def _function_relationships(
        self,
        graph: RepositoryGraph,
    ):

        # ---------------------------------------------
        # Build lookup:
        # function name -> qualified name
        # Example:
        # build_graph -> GraphService.build_graph
        # retrieve -> RepositoryRetriever.retrieve
        # ---------------------------------------------

        function_lookup = {}

        for fn in graph.functions.values():
            function_lookup[fn.name] = fn.qualified_name

        # ---------------------------------------------
        # Build relationships
        # ---------------------------------------------

        for function in graph.functions.values():

            # File -> Function

            graph.relationships.append(
                Relationship(
                    source=function.file_path,
                    target=function.qualified_name,
                    relationship_type="HAS_FUNCTION",
                )
            )

            # Class -> Method

            if function.class_name:

                graph.relationships.append(
                    Relationship(
                        source=function.class_name,
                        target=function.qualified_name,
                        relationship_type="HAS_METHOD",
                    )
                )

            # Function -> Function (CALLS)

            for called_function in function.calls:

                # calls may be dictionaries or plain strings

                if isinstance(called_function, dict):
                    called_name = called_function.get("name")
                else:
                    called_name = called_function

                target = function_lookup.get(called_name)

                if target:

                    graph.relationships.append(
                        Relationship(
                            source=function.qualified_name,
                            target=target,
                            relationship_type="CALLS",
                        )
                    )

    # =====================================================
    # Class Inheritance
    # =====================================================

    def _inheritance_relationships(
        self,
        graph: RepositoryGraph,
    ):

        repository_classes = set(
            graph.classes.keys()
        )

        for cls in graph.classes.values():

            for parent in cls.base_classes:

                if parent in repository_classes:

                    graph.relationships.append(
                        Relationship(
                            source=cls.name,
                            target=parent,
                            relationship_type="INHERITS",
                        )
                    )