from __future__ import annotations

from tree_sitter import Node

from app.extractor.parameter_extractor import ParameterExtractor
from app.extractor.call_extractor import CallExtractor
from app.extractor.dependency_extractor import DependencyExtractor


class FunctionExtractor:
    """
    Extracts Python function information.

    Extracted Information
    ---------------------
    - Qualified Name
    - Function Name
    - Parameters
    - Return Type
    - Decorators
    - Function Calls
    - Function Properties
    - Source Code
    - Line Numbers
    """

    def __init__(self):

        self.parameter_extractor = ParameterExtractor()

        self.call_extractor = CallExtractor()

        self.dependency_extractor = DependencyExtractor()

    def extract(
        self,
        node: Node,
        source_code: str,
        current_class: str | None,
    ) -> dict:

        function_name = ""

        parameters = []

        calls = []

        dependencies = []

        decorators = []

        return_type = None

        # ---------------------------------------------
        # Function Type
        # ---------------------------------------------

        is_async = (
            node.type == "async_function_definition"
        )

        # ---------------------------------------------
        # Traverse Function Children
        # ---------------------------------------------

        for child in node.children:

            # -----------------------------------------
            # Function Name
            # -----------------------------------------

            if child.type == "identifier":

                function_name = source_code[
                    child.start_byte:
                    child.end_byte
                ]

            # -----------------------------------------
            # Parameters
            # -----------------------------------------

            elif child.type == "parameters":

                parameters = self.parameter_extractor.extract(
                    child,
                    source_code,
                )

            # -----------------------------------------
            # Return Type
            # -----------------------------------------

            elif child.type == "type":

                return_type = source_code[
                    child.start_byte:
                    child.end_byte
                ]

            # -----------------------------------------
            # Decorators
            # -----------------------------------------

            elif child.type == "decorator":

                decorators.append(

                    source_code[
                        child.start_byte:
                        child.end_byte
                    ]

                )

            # -----------------------------------------
            # Function Body
            # -----------------------------------------

            elif child.type == "block":

                calls = self.call_extractor.extract(
                    child,
                    source_code,
                )

                dependencies = self.dependency_extractor.extract(
                    child,
                    source_code,

                )

        # ---------------------------------------------
        # Qualified Name
        # ---------------------------------------------

        qualified_name = (

            f"{current_class}.{function_name}"

            if current_class

            else function_name

        )

        # ---------------------------------------------
        # Function Properties
        # ---------------------------------------------

        is_method = current_class is not None

        visibility = (
            "private"
            if function_name.startswith("_")
            else "public"
        )

        is_static = any(
            "staticmethod" in decorator
            for decorator in decorators
        )

        is_classmethod = any(
            "classmethod" in decorator
            for decorator in decorators
        )

        # ---------------------------------------------
        # Return
        # ---------------------------------------------

        return {

            "qualified_name": qualified_name,

            "name": function_name,

            "class_name": current_class,

            # ---------------------------------
            # Function Properties
            # ---------------------------------

            "is_method": is_method,

            "is_async": is_async,

            "visibility": visibility,

            "is_static": is_static,

            "is_classmethod": is_classmethod,

            # ---------------------------------
            # Signature
            # ---------------------------------

            "parameters": parameters,

            "returns": return_type,

            # ---------------------------------
            # Behavior
            # ---------------------------------

            "decorators": decorators,

            "calls": calls,

            "dependencies": dependencies,

            # ---------------------------------
            # Source Location
            # ---------------------------------

            "start_line": node.start_point[0] + 1,

            "end_line": node.end_point[0] + 1,

            # ---------------------------------
            # Source Code
            # ---------------------------------

            "code": source_code[
                node.start_byte:
                node.end_byte
            ],
        }