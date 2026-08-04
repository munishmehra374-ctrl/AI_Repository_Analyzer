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

        match = re.search(

            r"[A-Za-z_][A-Za-z0-9_]*\.[A-Za-z_][A-Za-z0-9_]*",

            question,

        )

        if not match:

            return None

        qualified_name = match.group()

        function = self.graph.get_function(
            qualified_name
        )

        if function:

            return {

                "type": "function",

                "name": qualified_name,

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

            r"[A-Za-z0-9_]+\.py",

            question,

        )

        if not match:

            return None

        return {

            "type": "file",

            "name": match.group(),

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

        question = question.lower()

        for keyword in keywords:

            if keyword in question:

                return {

                    "type": "repository",

                    "name": "repository",

                }

        return None