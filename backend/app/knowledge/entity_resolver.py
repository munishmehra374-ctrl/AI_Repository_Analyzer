from __future__ import annotations

import re

from app.knowledge.graph_queries import GraphQueries


class EntityResolver:
    """
    Resolves repository entities mentioned in a user query.

    Supported entities
    ------------------
    - Repository
    - File
    - Class
    - Function
    """

    def __init__(
        self,
        graph_queries: GraphQueries,
    ):
        self.graph = graph_queries

        # Debug only
        self.graph.debug_functions()

    # =====================================================
    # Public API
    # =====================================================

    def resolve(
        self,
        question: str,
    ) -> dict:

        entity = (
            self._resolve_function(question)
            or self._resolve_class(question)
            or self._resolve_file(question)
            or self._resolve_repository(question)
        )

        return entity or {
            "type": None,
            "name": None,
        }

    # =====================================================
    # Function
    # =====================================================

    def _resolve_function(
        self,
        question: str,
    ):

        # =================================================
        # Qualified function
        # =================================================

        qualified_matches = re.findall(
            r"\b([A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*)\s*\(",
            question,
        )

        for qualified_name in qualified_matches:

            print(
                "FUNCTION DETECTED:",
                qualified_name,
            )

            function = self.graph.get_function(
                qualified_name
            )

            print(
                "FUNCTION FROM NEO4J:",
                function,
            )

            if function:

                return {
                    "type": "function",
                    "name": qualified_name,
                }

        # =================================================
        # Simple function
        # =================================================

        function_matches = re.findall(
            r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(",
            question,
        )

        for function_name in function_matches:

            print(
                "FUNCTION DETECTED:",
                function_name,
            )

            function = self.graph.get_function(
                function_name
            )

            print(
                "FUNCTION FROM NEO4J:",
                function,
            )

            if function:

                return {
                    "type": "function",
                    "name": function_name,
                }

        return None

    # =====================================================
    # Class
    # =====================================================

    def _resolve_class(
        self,
        question: str,
    ):

        matches = re.findall(
            r"\b[A-Z][A-Za-z0-9_]+\b",
            question,
        )

        for class_name in matches:

            cls = self.graph.get_class(
                class_name
            )

            if cls:

                return {
                    "type": "class",
                    "name": class_name,
                }

        return None

    # =====================================================
    # File
    # =====================================================

    def _resolve_file(
        self,
        question: str,
    ):

        match = re.search(
            r"\b[A-Za-z0-9_]+\.py\b",
            question,
        )

        if not match:
            return None

        file_name = match.group()

        print(
            "FILE DETECTED:",
            file_name,
        )

        file = self.graph.get_file_by_name(
            file_name
        )

        print(
            "FILE FROM NEO4J:",
            file,
        )

        if not file:
            return None

        return {
            "type": "file",
            "name": file["path"],
        }
    # =====================================================
    # Repository
    # =====================================================

    def _resolve_repository(
        self,
        question: str,
    ):

        keywords = [
            "repository",
            "project",
            "architecture",
            "structure",
            "overview",
        ]

        question_lower = question.lower()

        for keyword in keywords:

            if keyword in question_lower:

                return {
                    "type": "repository",
                    "name": "repository",
                }

        return None