from __future__ import annotations

from tree_sitter import Node


class DependencyExtractor:
    """
    Extracts constructor-based object dependencies.

    Supported patterns
    ------------------

    1. Constructor assignment:

        self.db = Database()

    2. Dependency injection through type annotations:

        def __init__(
            self,
            retriever: RetrievalService,
            reranker: CrossEncoderReranker,
        ):
            ...

    Does NOT extract normal method calls such as:

        query = query.lower()

        result = self.repo.get_summary()

        documents = retriever.retrieve(question)
    """

    # =====================================================
    # Tree-sitter BYTE SAFE SOURCE EXTRACTION
    # =====================================================

    @staticmethod
    def _get_text(
        node: Node,
        source_code: str,
    ) -> str:

        source_bytes = source_code.encode("utf-8")

        return source_bytes[
            node.start_byte:
            node.end_byte
        ].decode(
            "utf-8",
            errors="replace",
        )

    # =====================================================
    # Public API
    # =====================================================

    def extract(
        self,
        node: Node,
        source_code: str,
    ) -> list[dict]:

        print("🔥 DEPENDENCY EXTRACTOR CALLED 🔥")

        dependencies = []

        self._traverse(
            node=node,
            source_code=source_code,
            dependencies=dependencies,
        )

        return dependencies

    # =====================================================
    # Typed Parameter Extraction
    # =====================================================

    def _extract_typed_parameter(
        self,
        node: Node,
        source_code: str,
        dependencies: list,
    ):

        # -------------------------------------------------
        # First try Tree-sitter field names.
        # -------------------------------------------------

        variable_node = (
            node.child_by_field_name("name")
        )

        type_node = (
            node.child_by_field_name("type")
        )

        # -------------------------------------------------
        # Fallback:
        #
        # Some Tree-sitter structures expose the
        # identifier/type directly as children rather
        # than through the expected field names.
        # -------------------------------------------------

        if variable_node is None:

            for child in node.children:

                if child.type == "identifier":

                    variable_node = child

                    break

        if type_node is None:

            for child in node.children:

                if child.type in (
                    "type",
                    "generic_type",
                    "type_identifier",
                ):

                    type_node = child

                    break

        # -------------------------------------------------
        # If we still don't have a type node, stop.
        # -------------------------------------------------

        if type_node is None:

            return

        class_name = (
            self._get_text(
                type_node,
                source_code,
            ).strip()
        )

        # -------------------------------------------------
        # We are interested in class-like dependencies.
        #
        # Examples:
        #
        # HybridRetriever
        # ReciprocalRankFusion
        # CrossEncoderReranker
        # ContextOptimizer
        # EntityResolver
        #
        # Ignore:
        #
        # str
        # int
        # bool
        # -------------------------------------------------

        if not class_name:
            return

        if not class_name[0].isupper():
            return

        variable = ""

        if variable_node is not None:

            variable = (
                self._get_text(
                    variable_node,
                    source_code,
                ).strip()
            )

        dependency = {
            "variable": variable,
            "class": class_name,
        }

        # -------------------------------------------------
        # Avoid duplicates
        # -------------------------------------------------

        if dependency in dependencies:

            return

        dependencies.append(
            dependency
        )

        print(
            "DEPENDENCY FOUND:",
            variable,
            "->",
            class_name,
        )

    # =====================================================
    # Recursive Traversal
    # =====================================================

    def _traverse(
        self,
        node: Node,
        source_code: str,
        dependencies: list,
    ):

        # =================================================
        # 1. TYPE-ANNOTATED PARAMETERS
        # =================================================

        if node.type in (
            "typed_parameter",
            "typed_default_parameter",
        ):

            self._extract_typed_parameter(
                node=node,
                source_code=source_code,
                dependencies=dependencies,
            )

        # =================================================
        # 2. CONSTRUCTOR ASSIGNMENT
        #
        # Example:
        #
        # self.db = Database()
        # graph = GraphBuilder()
        #
        # =================================================

        if node.type == "assignment":

            left = (
                node.child_by_field_name(
                    "left"
                )
            )

            right = (
                node.child_by_field_name(
                    "right"
                )
            )

            if (
                left is not None
                and right is not None
                and right.type == "call"
            ):

                function = (
                    right.child_by_field_name(
                        "function"
                    )
                )

                if function is not None:

                    dependency = None

                    # -------------------------------------
                    # Constructor Call
                    # -------------------------------------

                    if function.type == "identifier":

                        class_name = (
                            self._get_text(
                                function,
                                source_code,
                            ).strip()
                        )

                        if (
                            class_name
                            and class_name[0].isupper()
                        ):

                            variable = (
                                self._get_text(
                                    left,
                                    source_code,
                                ).strip()
                            )

                            dependency = {
                                "variable": variable,
                                "class": class_name,
                            }

                    # -------------------------------------
                    # Ignore method calls
                    # -------------------------------------

                    elif function.type == "attribute":

                        pass

                    # -------------------------------------
                    # Store dependency
                    # -------------------------------------

                    if (
                        dependency is not None
                        and dependency not in dependencies
                    ):

                        dependencies.append(
                            dependency
                        )

                        print(
                            "DEPENDENCY FOUND:",
                            dependency["variable"],
                            "->",
                            dependency["class"],
                        )

        # =================================================
        # Continue Traversal
        # =================================================

        for child in node.children:

            self._traverse(
                node=child,
                source_code=source_code,
                dependencies=dependencies,
            )