from __future__ import annotations

from tree_sitter import Node


class ClassExtractor:
    """
    Extracts Python class information.

    Extracted Information
    ---------------------
    - Qualified Name
    - Class Name
    - Base Classes
    - Decorators
    - Visibility
    - Source Code
    - Line Numbers
    """

    def extract(
        self,
        node: Node,
        source_code: str,
    ) -> dict:

        class_name = ""

        base_classes = []

        decorators = []

        # ---------------------------------------
        # Traverse Class Children
        # ---------------------------------------

        for child in node.children:

            # ---------------------------------------
            # Class Name
            # ---------------------------------------

            if child.type == "identifier":

                class_name = source_code[
                    child.start_byte:
                    child.end_byte
                ]

            # ---------------------------------------
            # Base Classes
            # ---------------------------------------

            elif child.type == "argument_list":

                base_classes = self._extract_base_classes(
                    child,
                    source_code,
                )

            # ---------------------------------------
            # Decorators
            # ---------------------------------------

            elif child.type == "decorator":

                decorators.append(

                    source_code[
                        child.start_byte:
                        child.end_byte
                    ]

                )

        # ---------------------------------------
        # Class Properties
        # ---------------------------------------

        qualified_name = class_name

        visibility = (
            "private"
            if class_name.startswith("_")
            else "public"
        )

        # ---------------------------------------
        # Return
        # ---------------------------------------

        return {

            "qualified_name": qualified_name,

            "name": class_name,

            "visibility": visibility,

            "base_classes": base_classes,

            "decorators": decorators,

            "start_line": node.start_point[0] + 1,

            "end_line": node.end_point[0] + 1,

            "code": source_code[
                node.start_byte:
                node.end_byte
            ],
        }

    # =====================================================
    # Base Classes
    # =====================================================

    def _extract_base_classes(
        self,
        node: Node,
        source_code: str,
    ) -> list[str]:

        parents = []

        for child in node.children:

            if child.type == "identifier":

                parents.append(

                    source_code[
                        child.start_byte:
                        child.end_byte
                    ]

                )

        return parents