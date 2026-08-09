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

        # ==================================================
        # Function Call
        # ==================================================

        if node.type == "call":

            function_node = node.child_by_field_name(
                "function"
            )

            if function_node:

                called_text = source_code[
                    function_node.start_byte:
                    function_node.end_byte
                ]

                print(
                    "CALL DETECTED:",
                    called_text,
                )

                # ==========================================
                # Simple function
                #
                # foo()
                # ==========================================

                if function_node.type == "identifier":

                    calls.append(
                        {
                            "type": "function",
                            "object": None,
                            "name": called_text,
                            "full_name": called_text,
                        }
                    )

                # ==========================================
                # Method / attribute call
                #
                # self.foo()
                # service.foo()
                # self.service.foo()
                # ==========================================

                elif function_node.type == "attribute":

                    full_name = called_text

                    parts = full_name.split(".")

                    method_name = parts[-1]

                    object_name = (
                        ".".join(parts[:-1])
                        if len(parts) > 1
                        else None
                    )

                    calls.append(
                        {
                            "type": "method",
                            "object": object_name,
                            "name": method_name,
                            "full_name": full_name,
                        }
                    )

                    print(
                        "METHOD CALL:",
                        full_name,
                        "| OBJECT:",
                        object_name,
                        "| METHOD:",
                        method_name,
                    )

        # ==================================================
        # Continue Traversal
        # ==================================================

        for child in node.children:

            self._extract_calls(
                node=child,
                source_code=source_code,
                calls=calls,
            )