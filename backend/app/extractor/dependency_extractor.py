from __future__ import annotations

from tree_sitter import Node


class DependencyExtractor:
    """
    Extracts constructor-based object dependencies.

    Examples
    --------

    self.db = Database()

    self.retriever = RetrievalService()

    graph = GraphBuilder()

    vector_store = ChromaStore()

    Does NOT extract:

    query = query.lower()

    result = self.repo.get_summary()

    documents = retriever.retrieve(question)
    """

    def extract(
        self,
        node: Node,
        source_code: str,
    ) -> list[dict]:

        dependencies = []

        self._traverse(
            node=node,
            source_code=source_code,
            dependencies=dependencies,
        )

        return dependencies

    # =====================================================
    # Recursive Traversal
    # =====================================================

    def _traverse(
        self,
        node: Node,
        source_code: str,
        dependencies: list,
    ):

        # -------------------------------------------------
        # Assignment
        # -------------------------------------------------

        if node.type == "assignment":

            left = node.child_by_field_name("left")
            right = node.child_by_field_name("right")

            if (
                left is not None
                and right is not None
                and right.type == "call"
            ):

                function = right.child_by_field_name(
                    "function"
                )

                if function is None:
                    return

                dependency = None

                # -----------------------------------------
                # Constructor Call
                #
                # self.db = Database()
                # graph = GraphBuilder()
                # -----------------------------------------

                if function.type == "identifier":

                    class_name = source_code[
                        function.start_byte:
                        function.end_byte
                    ]

                    # Only consider ClassName()
                    if (
                        class_name
                        and class_name[0].isupper()
                    ):

                        dependency = {

                            "variable": source_code[
                                left.start_byte:
                                left.end_byte
                            ],

                            "class": class_name,
                        }

                # -----------------------------------------
                # Ignore Method Calls
                #
                # obj.lower()
                # self.repo.get_summary()
                # retriever.retrieve()
                # -----------------------------------------

                elif function.type == "attribute":

                    pass

                if dependency is not None:

                    dependencies.append(
                        dependency
                    )

        # -------------------------------------------------
        # Continue Traversal
        # -------------------------------------------------

        for child in node.children:

            self._traverse(
                child,
                source_code,
                dependencies,
            )