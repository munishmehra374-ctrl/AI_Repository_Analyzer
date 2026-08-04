from __future__ import annotations

from tree_sitter import Node


class CallExtractor:
    """
    Extracts function and method calls.

    Examples
    --------

    foo()

    self.bar()

    obj.method()

    repository.save()

    vector_store.add_documents()
    """

    def extract(
        self,
        node: Node,
        source_code: str,
    ) -> list[dict]:

        calls = []

        self._extract_calls(
            node=node,
            source_code=source_code,
            calls=calls,
        )

        return calls

    # ======================================================
    # Recursive Traversal
    # ======================================================

    def _extract_calls(
        self,
        node: Node,
        source_code: str,
        calls: list,
    ):

        # --------------------------------------------
        # Function Call
        # --------------------------------------------

        if node.type == "call":

            function_node = node.child_by_field_name(
                "function"
            )

            if function_node:

                # ------------------------------------
                # foo()
                # ------------------------------------

                if function_node.type == "identifier":

                    calls.append(
                        {
                            "type": "function",
                            "object": None,
                            "name": source_code[
                                function_node.start_byte:
                                function_node.end_byte
                            ],
                        }
                    )

                # ------------------------------------
                # object.method()
                # ------------------------------------

                elif function_node.type == "attribute":

                    identifiers = []

                    for child in function_node.children:

                        if child.type == "identifier":

                            identifiers.append(

                                source_code[
                                    child.start_byte:
                                    child.end_byte
                                ]

                            )

                    object_name = None
                    method_name = None

                    if len(identifiers) >= 2:

                        object_name = identifiers[0]

                        method_name = identifiers[-1]

                    elif len(identifiers) == 1:

                        method_name = identifiers[0]

                    calls.append(
                        {
                            "type": "method",
                            "object": object_name,
                            "name": method_name,
                        }
                    )

        # --------------------------------------------
        # Continue Traversal
        # --------------------------------------------

        for child in node.children:

            self._extract_calls(
                child,
                source_code,
                calls,
            )