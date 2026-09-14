from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
from app.knowledge.models import Relationship, RepositoryGraph


class RelationshipBuilder:
    """Builds structural relationships for the RepositoryGraph."""

    def build(self, graph: RepositoryGraph) -> RepositoryGraph:

        print("\n========== RELATIONSHIP BUILDER FILE ==========")
        print(__file__)
        print("===============================================")
        # Clear existing relationships to avoid duplicates on re-runs
        graph.relationships.clear()

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

    def _repository_relationships(self, graph: RepositoryGraph) -> None:
        if graph.repository is None:
            return

        for folder_path in graph.folders.keys():
            graph.relationships.append(
                Relationship(
                    source=graph.repository.path,
                    target=folder_path,
                    relationship_type="HAS_FOLDER",
                )
            )

    # =====================================================
    # Folder -> File
    # =====================================================

    def _file_relationships(self, graph: RepositoryGraph) -> None:
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

    def _import_relationships(self, graph: RepositoryGraph) -> None:
        seen = set()
        for imp in graph.imports.values():
            if not imp.file_path or not imp.statement:
                continue

            key = (imp.file_path, imp.statement)
            if key in seen:
                continue
            seen.add(key)

            graph.relationships.append(
                Relationship(
                    source=imp.file_path,
                    target=imp.statement,
                    relationship_type="IMPORTS",
                )
            )

    # =====================================================
    # File -> Class
    # =====================================================

    def _class_relationships(self, graph: RepositoryGraph) -> None:
        for cls in graph.classes.values():
            if not cls.file_path:
                continue

            target_identifier = cls.qualified_name or cls.name
            graph.relationships.append(
                Relationship(
                    source=cls.file_path,
                    target=target_identifier,
                    relationship_type="HAS_CLASS",
                )
            )

    # =====================================================
    # Class -> Parent Class (INHERITS)
    # =====================================================

    def _inheritance_relationships(self, graph: RepositoryGraph) -> None:
        for cls in graph.classes.values():
            if not cls.base_classes:
                continue

            source_cls = cls.qualified_name or cls.name
            for parent_class in cls.base_classes:
                if not parent_class:
                    continue

                graph.relationships.append(
                    Relationship(
                        source=source_cls,
                        target=parent_class,
                        relationship_type="INHERITS",
                    )
                )

    # =====================================================
    # File -> Function / Method / Dependencies / Calls
    # =====================================================

    def _function_relationships(self, graph: RepositoryGraph) -> None:

        print("\n========== FUNCTION RELATIONSHIPS ENTERED ==========")
        print("Total functions:", len(graph.functions))
        # Pre-build lookup tables for O(1) resolution
        fn_by_qualified: Dict[str, str] = {}
        fn_by_simple_name: Dict[str, List[str]] = {}
        class_lookup: Dict[str, str] = {}

        # 1. Class Lookup Indexing
        for key, cls in graph.classes.items():
            class_lookup[key] = cls.name
            class_lookup[cls.name] = cls.name
            if cls.qualified_name:
                class_lookup[cls.qualified_name] = cls.name

        # 2. Function Indexing
        for function in graph.functions.values():
            qname = function.qualified_name
            sname = function.name

            if qname:
                fn_by_qualified[qname] = qname

            if sname:
                fn_by_simple_name.setdefault(sname, []).append(qname or sname)

                print("\n========== FUNCTION INDEX DEBUG ==========")

        print(
            "TreeSitterParser.parse exists:",
            "TreeSitterParser.parse" in fn_by_qualified
        )

        print("TreeSitterParser functions:")

        for name in fn_by_qualified:
            if "TreeSitterParser" in name:
                print("   ", name)

        print(
            "Total indexed functions:",
            len(fn_by_qualified)
        )

        print("==========================================\n")


        # 3. Relationship Construction
        for function in graph.functions.values():
            func_identifier = function.qualified_name or function.name

            # File -> Function
            if function.file_path:
                graph.relationships.append(
                    Relationship(
                        source=function.file_path,
                        target=func_identifier,
                        relationship_type="HAS_FUNCTION",
                    )
                )

            # Class -> Method
            if function.class_name:
                graph.relationships.append(
                    Relationship(
                        source=function.class_name,
                        target=func_identifier,
                        relationship_type="HAS_METHOD",
                    )
                )

                # Class -> Dependency (O(1) dictionary hit)
                if function.dependencies:
                    self._resolve_class_dependencies(
                        graph, function.class_name, function.dependencies, class_lookup
                    )

            # Function -> Function (CALLS)
            self._resolve_function_calls(
                graph,
                function,
                func_identifier,
                fn_by_qualified,
                fn_by_simple_name,
                class_lookup,
            )
    # =====================================================
    # Class Dependency Resolver
    # =====================================================

    def _resolve_class_dependencies(
        self,
        graph: RepositoryGraph,
        class_name: str,
        dependencies: List[dict],
        class_lookup: Dict[str, str],
    ) -> None:
        for dependency in dependencies:
            if not isinstance(dependency, dict):
                continue

            dep_class_raw = dependency.get("class")
            if not dep_class_raw:
                continue

            resolved_target = class_lookup.get(dep_class_raw)
            if resolved_target:
                graph.relationships.append(
                    Relationship(
                        source=class_name,
                        target=resolved_target,
                        relationship_type="DEPENDS_ON",
                    )
                )

    # =====================================================
    # Function Call Resolver
    # =====================================================
    def _resolve_function_calls(
        self,
        graph: RepositoryGraph,
        function: Any,
        caller_id: str,
        fn_by_qualified: Dict[str, str],
        fn_by_simple_name: Dict[str, List[str]],
        class_lookup: Dict[str, str],
    ) -> None:

        print("\n========== CALL RESOLUTION ENTERED ==========")
        print("Function:", caller_id)
        print("Calls:", function.calls)

        # Build dependency lookup:
        # self.parser -> TreeSitterParser
        # self.extractor -> ASTExtractor
        # self.chunker -> SemanticChunker

        dependency_classes = {}

        for dependency in function.dependencies or []:

            if not isinstance(dependency, dict):
                continue

            variable = dependency.get("variable")
            dep_class = dependency.get("class")

            if variable and dep_class:
                dependency_classes[variable] = dep_class

        print("Dependency classes:", dependency_classes)

        for called in function.calls:

            if isinstance(called, dict):
                called_name = called.get("name")
                full_name = called.get("full_name")
                object_name = called.get("object")
            else:
                called_name = str(called)
                full_name = str(called)
                object_name = None

            if not called_name:
                continue

            target: Optional[str] = None

            # =================================================
            # 1. self.object.method()
            #
            # Example:
            # self.parser.parse()
            #
            # self.parser -> TreeSitterParser
            # parse       -> TreeSitterParser.parse
            # =================================================

            if object_name and object_name.startswith("self."):

                dependency_variable = object_name

                dependency_class = dependency_classes.get(
                    dependency_variable
                )

                if dependency_class:

                    candidate = (
                        f"{dependency_class}.{called_name}"
                    )

                    if candidate in fn_by_qualified:

                        target = fn_by_qualified[
                            candidate
                        ]

                        print(
                            f"[DEPENDENCY CALL RESOLVED] "
                            f"{caller_id} -> {target}"
                        )

            # =================================================
            # 2. Direct self.method()
            # =================================================

            if target is None:

                if (
                    object_name == "self"
                    and function.class_name
                ):

                    candidate = (
                        f"{function.class_name}."
                        f"{called_name.removeprefix('self.')}"
                    )

                    if candidate in graph.functions:

                        target = candidate

            # =================================================
            # 3. Exact qualified name
            # =================================================

            if target is None:

                if called_name in fn_by_qualified:

                    target = fn_by_qualified[
                        called_name
                    ]

            # =================================================
            # 4. Full name
            # =================================================

            if target is None:

                if (
                    full_name
                    and full_name in fn_by_qualified
                ):

                    target = fn_by_qualified[
                        full_name
                    ]

            # =================================================
            # 5. Simple name fallback
            # =================================================

            if target is None:

                if called_name in fn_by_simple_name:

                    candidates = fn_by_simple_name[
                        called_name
                    ]

                    same_file = [
                        cand
                        for cand in candidates
                        if (
                            cand in graph.functions
                            and
                            graph.functions[cand].file_path
                            == function.file_path
                        )
                    ]

                    if len(same_file) == 1:

                        target = same_file[0]

                    elif len(candidates) == 1:

                        target = candidates[0]

            # =================================================
            # 6. Create relationship
            # =================================================

            if target:

                print(
                    f"[CALL RESOLVED] "
                    f"{caller_id} -> {target}"
                )

                graph.relationships.append(
                    Relationship(
                        source=caller_id,
                        target=target,
                        relationship_type="CALLS",
                    )
                )

            else:

                print(
                    f"[CALL UNRESOLVED] "
                    f"{caller_id} -> {called_name} "
                    f"(object: {object_name})"
                )