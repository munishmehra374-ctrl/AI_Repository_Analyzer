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
    Builds an in-memory RepositoryGraph.

    Responsibilities
    ----------------
    - Create graph nodes.
    - Build structural relationships.
    - Analyze semantic relationships.
    """

    def __init__(self):
        self.relationship_builder = RelationshipBuilder()
        self.dependency_analyzer = DependencyAnalyzer()
        self.import_analyzer = ImportAnalyzer()
        self.inheritance_analyzer = InheritanceAnalyzer()

    def build(
        self,
        extracted: dict,
    ) -> RepositoryGraph:

        graph = RepositoryGraph()

        # ==================================================
        # Repository
        # ==================================================

        repository_name = extracted.get(
            "repository_name",
            "repository",
        )

        repository_path = extracted.get(
            "repository_path",
            repository_name,
        )

        graph.repository = RepositoryNode(
            name=repository_name,
            path=repository_path,
        )

        # ==================================================
        # Folder
        # ==================================================

        file_path = extracted.get(
            "file_path",
            "",
        )

        
        print("file_path =", repr(file_path))

        folder_path = os.path.dirname(
            file_path,
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

        # ==================================================
        # File
        # ==================================================

        if file_path:
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

        # ==================================================
        # Imports
        # ==================================================

        for imported_module in extracted.get(
            "imports",
            [],
        ):
            graph.imports[
                imported_module["statement"]
            ] = ImportNode(
                statement=imported_module[
                    "statement"
                ]
            )

        # ==================================================
        # Classes
        # ==================================================

        for cls in extracted.get(
            "classes",
            [],
        ):
            graph.classes[
                cls["qualified_name"]
            ] = ClassNode(
                qualified_name=cls["qualified_name"],
                name=cls["name"],
                file_path=file_path,
                visibility=cls["visibility"],
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
        # ==================================================
        # Functions
        # ==================================================

        for function in extracted.get(
            "functions",
            [],
        ):
            graph.functions[
                function["qualified_name"]
            ] = FunctionNode(
                qualified_name=function["qualified_name"],
                name=function["name"],
                file_path=file_path,
                class_name=function["class_name"],

                # ---------------------------------
                # Function Properties
                # ---------------------------------

                is_method=function["is_method"],
                is_async=function["is_async"],
                visibility=function["visibility"],
                is_static=function["is_static"],
                is_classmethod=function["is_classmethod"],

                # ---------------------------------
                # Signature
                # ---------------------------------

                parameters=function.get(
                    "parameters",
                    [],
                ),

                returns=function.get(
                    "returns",
                ),

                # ---------------------------------
                # Behavior
                # ---------------------------------

                calls=[
                    call["name"]
                    if isinstance(call, dict)
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

                # ---------------------------------
                # Location
                # ---------------------------------

                start_line=function["start_line"],
                end_line=function["end_line"],

                # ---------------------------------
                # Source
                # ---------------------------------

                code=function["code"],
            )

        # ==================================================
        # Routes (Future)
        # ==================================================

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

        # ==================================================
        # Models (Future)
        # ==================================================

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

        # ==================================================
        # Structural Relationships
        # ==================================================

        graph = self.relationship_builder.build(
            graph
        )

        # ==================================================
        # Semantic Relationships
        # ==================================================

        graph = self.dependency_analyzer.analyze(
            graph
        )

        graph = self.import_analyzer.analyze(
            graph
        )

        graph = self.inheritance_analyzer.analyze(
            graph
        )

        print("Files in graph:", len(graph.files))

        return graph