from __future__ import annotations

import os

from app.knowledge.models import (
    RepositoryGraph,
    RepositoryNode,
    FolderNode,
    FileNode,
    ImportNode,
    ClassNode,
    FunctionNode,
    RouteNode,
    ModelNode,
)

from app.knowledge.relationship_builder import RelationshipBuilder
from app.knowledge.dependency_analyzer import DependencyAnalyzer
from app.knowledge.import_analyzer import ImportAnalyzer
from app.knowledge.inheritance_analyzer import InheritanceAnalyzer


class GraphBuilder:
    """
    Builds one RepositoryGraph for the entire repository.
    """

    def __init__(self):

        self.relationship_builder = RelationshipBuilder()
        self.dependency_analyzer = DependencyAnalyzer()
        self.import_analyzer = ImportAnalyzer()
        self.inheritance_analyzer = InheritanceAnalyzer()

    # =====================================================
    # Build Entire Repository
    # =====================================================

    def build_repository(
        self,
        extracted_files: list[dict],
    ) -> RepositoryGraph:

        graph = RepositoryGraph()

        if not extracted_files:
            return graph

        # =================================================
        # Repository information
        # =================================================

        first = extracted_files[0]

        repository_name = first.get(
            "repository_name",
            "repository",
        )

        repository_path = first.get(
            "repository_path",
            repository_name,
        )

        graph.repository = RepositoryNode(
            name=repository_name,
            path=repository_path,
        )

        # =================================================
        # Process every file
        # =================================================

        for extracted in extracted_files:

            self._add_file_to_graph(
                graph,
                extracted,
            )

        # =================================================
        # Build relationships ONLY AFTER
        # ALL FUNCTIONS ARE IN THE GRAPH
        # =================================================

        graph = self.relationship_builder.build(
            graph
        )

        # =================================================
        # Semantic relationships
        # =================================================

        graph = self.dependency_analyzer.analyze(
            graph
        )

        graph = self.import_analyzer.analyze(
            graph
        )

        graph = self.inheritance_analyzer.analyze(
            graph
        )

        print(
            "=============================================="
        )

        print(
            "FINAL REPOSITORY GRAPH"
        )

        print(
            "FILES:",
            len(graph.files),
        )

        print(
            "CLASSES:",
            len(graph.classes),
        )

        print(
            "FUNCTIONS:",
            len(graph.functions),
        )

        print(
            "RELATIONSHIPS:",
            len(graph.relationships),
        )

        print(
            "CALL RELATIONSHIPS:",
            sum(
                1
                for relationship
                in graph.relationships
                if relationship.relationship_type
                == "CALLS"
            ),
        )

        print(
            "=============================================="
        )

        return graph

    # =====================================================
    # Add One File
    # =====================================================

    def _add_file_to_graph(
        self,
        graph: RepositoryGraph,
        extracted: dict,
    ):

        file_path = extracted.get(
            "file_path",
            "",
        )

        if not file_path:
            return

        # =================================================
        # Folder
        # =================================================

        folder_path = os.path.dirname(
            file_path
        )

        if folder_path:

            graph.folders[
                folder_path
            ] = FolderNode(
                name=os.path.basename(
                    folder_path
                ),
                path=folder_path,
            )

        # =================================================
        # File
        # =================================================

        graph.files[
            file_path
        ] = FileNode(
            name=os.path.basename(
                file_path
            ),
            path=file_path,
            language=extracted.get(
                "language",
                "python",
            ),
        )

        # =================================================
        # Imports
        # =================================================

        for imported_module in extracted.get(
            "imports",
            [],
        ):

            statement = imported_module.get(
                "statement"
            )

            if not statement:
                continue

            graph.imports[
                statement
            ] = ImportNode(
                statement=statement,
                module=imported_module.get(
                    "module"
                ),
                alias=imported_module.get(
                    "alias"
                ),
                file_path=file_path,
            )

        # =================================================
        # Classes
        # =================================================

        for cls in extracted.get(
            "classes",
            [],
        ):

            qualified_name = cls.get(
                "qualified_name",
                cls["name"],
            )

            graph.classes[
                qualified_name
            ] = ClassNode(
                qualified_name=qualified_name,
                name=cls["name"],
                file_path=file_path,
                visibility=cls.get(
                    "visibility",
                    "public",
                ),
                base_classes=cls.get(
                    "base_classes",
                    [],
                ),
                decorators=cls.get(
                    "decorators",
                    [],
                ),
                start_line=cls["start_line"],
                end_line=cls["end_line"],
                code=cls["code"],
            )

        # =================================================
        # Functions
        # =================================================

        for function in extracted.get(
            "functions",
            [],
        ):

            qualified_name = function[
                "qualified_name"
            ]

            graph.functions[
                qualified_name
            ] = FunctionNode(

                qualified_name=qualified_name,

                name=function["name"],

                file_path=file_path,

                class_name=function[
                    "class_name"
                ],

                is_method=function[
                    "is_method"
                ],

                is_async=function[
                    "is_async"
                ],

                visibility=function[
                    "visibility"
                ],

                is_static=function[
                    "is_static"
                ],

                is_classmethod=function[
                    "is_classmethod"
                ],

                parameters=function.get(
                    "parameters",
                    [],
                ),

                returns=function.get(
                    "returns"
                ),

                calls=[
                    call.get("name")
                    if isinstance(
                        call,
                        dict,
                    )
                    else call
                    for call in function.get(
                        "calls",
                        [],
                    )
                ],

                dependencies=function.get(
                    "dependencies",
                    [],
                ),

                decorators=function.get(
                    "decorators",
                    [],
                ),

                start_line=function[
                    "start_line"
                ],

                end_line=function[
                    "end_line"
                ],

                code=function[
                    "code"
                ],
            )

        # =================================================
        # Routes
        # =================================================

        for route in extracted.get(
            "routes",
            [],
        ):

            graph.routes[
                route["path"]
            ] = RouteNode(
                method=route["method"],
                path=route["path"],
                handler=route["handler"],
            )

        # =================================================
        # Models
        # =================================================

        for model in extracted.get(
            "models",
            [],
        ):

            graph.models[
                model["name"]
            ] = ModelNode(
                name=model["name"],
                file_path=file_path,
            )