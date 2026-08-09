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

            folder = os.path.dirname(
                file.path
            )

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

        for imp in graph.imports.values():

            if not imp.file_path:
                continue

            graph.relationships.append(
                Relationship(
                    source=imp.file_path,
                    target=imp.statement,
                    relationship_type="IMPORTS",
                )
            )

            print(
                "IMPORTS RELATIONSHIP:",
                imp.file_path,
                "->",
                imp.statement,
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

        # =================================================
        # Build function lookup
        # =================================================

        function_lookup = {}

        for function in graph.functions.values():

            qualified_name = (
                function.qualified_name
            )

            function_name = (
                function.name
            )

            # ---------------------------------------------
            # Qualified name
            # ---------------------------------------------

            if qualified_name:

                function_lookup[
                    qualified_name
                ] = qualified_name

            # ---------------------------------------------
            # Simple name
            # ---------------------------------------------

            if function_name:

                function_lookup.setdefault(
                    function_name,
                    []
                )

                if isinstance(
                    function_lookup[
                        function_name
                    ],
                    list,
                ):

                    function_lookup[
                        function_name
                    ].append(
                        qualified_name
                    )

        # =================================================
        # Build relationships
        # =================================================

        for function in graph.functions.values():

            # ---------------------------------------------
            # File -> Function
            # ---------------------------------------------

            graph.relationships.append(
                Relationship(
                    source=function.file_path,
                    target=function.qualified_name,
                    relationship_type="HAS_FUNCTION",
                )
            )

            # ---------------------------------------------
            # Class -> Method
            # ---------------------------------------------

            if function.class_name:

                graph.relationships.append(
                    Relationship(
                        source=function.class_name,
                        target=function.qualified_name,
                        relationship_type="HAS_METHOD",
                    )
                )

            # ---------------------------------------------
            # Function -> Function
            # ---------------------------------------------

            for called_function in function.calls:

                # =========================================
                # Extract call name
                # =========================================

                if isinstance(
                    called_function,
                    dict,
                ):

                    called_name = (
                        called_function.get(
                            "name"
                        )
                    )

                    full_name = (
                        called_function.get(
                            "full_name"
                        )
                    )

                    object_name = (
                        called_function.get(
                            "object"
                        )
                    )

                else:

                    called_name = (
                        called_function
                    )

                    full_name = (
                        called_function
                    )

                    object_name = None

                if not called_name:
                    continue

                # =========================================
                # Normalize self.foo()
                # =========================================

                normalized_name = called_name

                if normalized_name.startswith(
                    "self."
                ):

                    normalized_name = (
                        normalized_name[
                            len("self.") :
                        ]
                    )

                # =========================================
                # DEBUG
                # =========================================

                print(
                    "\nCALL RESOLUTION"
                )

                print(
                    "CALLER:",
                    function.qualified_name,
                )

                print(
                    "CALLED NAME:",
                    called_name,
                )

                print(
                    "FULL NAME:",
                    full_name,
                )

                print(
                    "OBJECT:",
                    object_name,
                )

                # =========================================
                # Resolve target
                # =========================================

                target = None

                # -----------------------------------------
                # 1. Exact qualified name
                # -----------------------------------------

                if (
                    called_name
                    in function_lookup
                    and isinstance(
                        function_lookup[
                            called_name
                        ],
                        str,
                    )
                ):

                    target = function_lookup[
                        called_name
                    ]

                # -----------------------------------------
                # 2. Full qualified expression
                # -----------------------------------------

                if target is None and full_name:

                    if (
                        full_name
                        in function_lookup
                        and isinstance(
                            function_lookup[
                                full_name
                            ],
                            str,
                        )
                    ):

                        target = function_lookup[
                            full_name
                        ]

                # -----------------------------------------
                # 3. Simple function name
                # -----------------------------------------

                if target is None:

                    candidates = (
                        function_lookup.get(
                            called_name,
                            []
                        )
                    )

                    if isinstance(
                        candidates,
                        list,
                    ):

                        # ---------------------------------
                        # Prefer function from same file
                        # ---------------------------------

                        same_file_candidates = [
                            candidate
                            for candidate
                            in candidates
                            if graph.functions[
                                candidate
                            ].file_path
                            == function.file_path
                        ]

                        if len(
                            same_file_candidates
                        ) == 1:

                            target = (
                                same_file_candidates[
                                    0
                                ]
                            )

                        elif len(
                            candidates
                        ) == 1:

                            target = (
                                candidates[0]
                            )

                # =========================================
                # 4. Resolve self.method()
                # =========================================

                if (
                    target is None
                    and object_name == "self"
                    and function.class_name
                ):

                    candidate = (
                        f"{function.class_name}."
                        f"{called_name}"
                    )

                    if candidate in graph.functions:

                        target = candidate

                # =========================================
                # Create CALLS relationship
                # =========================================

                if target:

                    graph.relationships.append(
                        Relationship(
                            source=function.qualified_name,
                            target=target,
                            relationship_type="CALLS",
                        )
                    )

                    print(
                        "CALLS RELATIONSHIP:",
                        function.qualified_name,
                        "->",
                        target,
                    )

                else:

                    print(
                        "CALL TARGET NOT FOUND:",
                        called_name,
                    )

    # =====================================================
    # Class Inheritance
    # =====================================================

    def _inheritance_relationships(
        self,
        graph: RepositoryGraph,
    ):

        # -------------------------------------------------
        # Build lookup using both qualified and simple names
        # -------------------------------------------------

        class_lookup = {}

        for cls in graph.classes.values():

            # Qualified name
            if cls.qualified_name:
                class_lookup[
                    cls.qualified_name
                ] = cls

            # Simple name
            if cls.name:
                class_lookup.setdefault(
                    cls.name,
                    cls,
                )

        # -------------------------------------------------
        # Resolve inheritance relationships
        # -------------------------------------------------

        for cls in graph.classes.values():

            for parent in cls.base_classes:

                if not parent:
                    continue

                parent_class = class_lookup.get(
                    parent
                )

                if parent_class is None:
                    continue

                graph.relationships.append(
                    Relationship(
                        source=cls.name,
                        target=parent_class.name,
                        relationship_type="INHERITS",
                    )
                )

                print(
                    "INHERITS RELATIONSHIP:",
                    cls.name,
                    "->",
                    parent_class.name,
                )