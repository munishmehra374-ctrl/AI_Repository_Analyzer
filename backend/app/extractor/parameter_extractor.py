from __future__ import annotations

from tree_sitter import Node


class ParameterExtractor:
    """
    Extracts function parameters.

    Supports:

    def foo(a, b)

    def foo(a: int, b: str)

    def foo(self, x: list[int])
    """

    def extract(
        self,
        node: Node,
        source_code: str,
    ) -> list[dict]:

        parameters = []

        for child in node.children:

            # -----------------------------
            # Normal parameter
            # -----------------------------

            if child.type == "identifier":

                parameters.append(
                    {
                        "name": source_code[
                            child.start_byte:child.end_byte
                        ],
                        "type": None,
                    }
                )

            # -----------------------------
            # Typed parameter
            # -----------------------------

            elif child.type == "typed_parameter":

                parameter_name = None
                parameter_type = None

                identifiers = []

                for parameter_child in child.children:

                    if parameter_child.type == "identifier":

                        identifiers.append(

                            source_code[
                                parameter_child.start_byte:
                                parameter_child.end_byte
                            ]

                        )

                if identifiers:

                    parameter_name = identifiers[0]

                    if len(identifiers) > 1:

                        parameter_type = identifiers[-1]

                parameters.append(
                    {
                        "name": parameter_name,
                        "type": parameter_type,
                    }
                )

        return parameters