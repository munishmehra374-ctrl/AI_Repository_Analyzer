from __future__ import annotations

from tree_sitter import Node

from app.extractor.parameter_extractor import ParameterExtractor
from app.extractor.call_extractor import CallExtractor
from app.extractor.dependency_extractor import DependencyExtractor


class FunctionExtractor:
    """
    Extracts Python function information.
    """

    def __init__(self):

        self.parameter_extractor = ParameterExtractor()

        self.call_extractor = CallExtractor()

        self.dependency_extractor = DependencyExtractor()

    # ==========================================================
    # Source Helper
    # ==========================================================

    @staticmethod
    def _get_source_text(
        node: Node,
        source_code: str,
    ) -> str:

        source_bytes = source_code.encode(
            "utf-8"
        )

        return source_bytes[
            node.start_byte:
            node.end_byte
        ].decode(
            "utf-8",
            errors="replace",
        )

    # ==========================================================
    # Extract Function
    # ==========================================================

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

        # ------------------------------------------------------
        # Function Type
        # ------------------------------------------------------

        is_async = (
            node.type
            == "async_function_definition"
        )

        # ------------------------------------------------------
        # Traverse Function Children
        # ------------------------------------------------------

        for child in node.children:

            # --------------------------------------------------
            # Function Name
            # --------------------------------------------------

            if child.type == "identifier":

                function_name = (
                    self._get_source_text(
                        child,
                        source_code,
                    )
                )

            # --------------------------------------------------
            # Parameters
            # --------------------------------------------------

            elif child.type == "parameters":

                parameters = (
                    self.parameter_extractor.extract(
                        child,
                        source_code,
                    )
                )

            # --------------------------------------------------
            # Return Type
            # --------------------------------------------------

            elif child.type == "type":

                return_type = (
                    self._get_source_text(
                        child,
                        source_code,
                    )
                )

            # --------------------------------------------------
            # Decorators
            # --------------------------------------------------

            elif child.type == "decorator":

                decorators.append(
                    self._get_source_text(
                        child,
                        source_code,
                    )
                )

            # --------------------------------------------------
            # Function Body
            # --------------------------------------------------

            elif child.type == "block":

                calls = (
                    self.call_extractor.extract(
                        child,
                        source_code,
                    )
                )

                print(
                    "FUNCTION:",
                    function_name,
                    "CALLS:",
                    calls,
                )

        # ------------------------------------------------------
        # Dependencies
        #
        # IMPORTANT:
        # Pass the COMPLETE function node.
        #
        # This allows DependencyExtractor to inspect:
        #
        # def __init__(
        #     self,
        #     retriever: RetrievalService,
        # ):
        #
        # as well as:
        #
        # self.db = Database()
        # ------------------------------------------------------

    # ------------------------------------------------------
# Dependencies
# ------------------------------------------------------

        print(
            "🔥 ABOUT TO EXTRACT DEPENDENCIES:",
            function_name,
            "CLASS:",
            current_class,
        )

        dependencies = (
            self.dependency_extractor.extract(
                node,
                source_code,
            )
        )

        print(
            "🔥 DEPENDENCIES RESULT:",
            function_name,
            dependencies,
        )

        # ------------------------------------------------------
        # Qualified Name
        # ------------------------------------------------------

        qualified_name = (

            f"{current_class}.{function_name}"

            if current_class

            else function_name

        )

        # ------------------------------------------------------
        # Function Properties
        # ------------------------------------------------------

        is_method = (
            current_class is not None
        )

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

        # ------------------------------------------------------
        # Return
        # ------------------------------------------------------

        return {

            "qualified_name": qualified_name,

            "name": function_name,

            "class_name": current_class,

            "is_method": is_method,

            "is_async": is_async,

            "visibility": visibility,

            "is_static": is_static,

            "is_classmethod": is_classmethod,

            "parameters": parameters,

            "returns": return_type,

            "decorators": decorators,

            "calls": calls,

            "dependencies": dependencies,

            "start_line": (
                node.start_point[0] + 1
            ),

            "end_line": (
                node.end_point[0] + 1
            ),

            "code": (
                self._get_source_text(
                    node,
                    source_code,
                )
            ),
        }