from __future__ import annotations

import re

from app.knowledge.graph_queries import GraphQueries


class EntityResolver:
    """
    Resolves repository entities mentioned in a natural-language query.

    Supported entities:
    - Repository
    - File
    - Class
    - Function

    The resolver does NOT contain project-specific class names,
    function names, or file names.

    Candidate identifiers are extracted from the user's question
    and verified against the repository knowledge graph.
    """

    def __init__(
        self,
        graph_queries: GraphQueries,
        repository_id: str,
    ):
        self.graph = graph_queries
        self.repository_id = repository_id

    # =====================================================
    # Public API
    # =====================================================

    def resolve(
        self,
        question: str,
    ) -> dict:
        """
        Resolve the most relevant repository entity mentioned
        in the user's question.

        Returns:

        {
            "type": "class" | "function" | "file" | "repository" | None,
            "name": str | None,
        }
        """

        if not question or not question.strip():
            return {
                "type": None,
                "name": None,
            }

        candidates = self._extract_candidates(
            question
        )

        print(
            "\n========== ENTITY RESOLUTION =========="
        )

        print(
            "Question:",
            question,
        )

        print(
            "Candidates:",
            candidates,
        )

        # -------------------------------------------------
        # Resolve candidates against Neo4j
        #
        # We check every candidate rather than trusting
        # the wording of the question.
        # -------------------------------------------------

        for candidate in candidates:

            if not candidate:
                continue

            # ---------------------------------------------
            # Function
            # ---------------------------------------------

            function = self.graph.get_function(
                candidate,
                repository_id=self.repository_id,
    )
            if function:

                print(
                    "ENTITY FOUND:",
                    candidate,
                )

                print(
                    "ENTITY TYPE: function"
                )

                print(
                    "========================================\n"
                )

                return {
                    "type": "function",
                    "name": candidate,
                }

            # ---------------------------------------------
            # Class
            # ---------------------------------------------

            cls = self.graph.get_class(
                candidate,
                repository_id=self.repository_id,
    )
            if cls:

                print(
                    "ENTITY FOUND:",
                    candidate,
                )

                print(
                    "ENTITY TYPE: class"
                )

                print(
                    "========================================\n"
                )

                return {
                    "type": "class",
                    "name": candidate,
                }

            # ---------------------------------------------
            # File
            # ---------------------------------------------

            if self._looks_like_file(candidate):

                file = self.graph.get_file_by_name(
                        candidate,
                        repository_id=self.repository_id,
    )
                if file:

                    file_path = self._node_value(
                        file,
                        "path",
                        candidate,
                    )

                    print(
                        "ENTITY FOUND:",
                        candidate,
                    )

                    print(
                        "ENTITY TYPE: file"
                    )

                    print(
                        "========================================\n"
                    )

                    return {
                        "type": "file",
                        "name": file_path,
                    }

        # -------------------------------------------------
        # Repository-level question
        # -------------------------------------------------

        repository = self._resolve_repository(
            question
        )

        if repository:

            print(
                "ENTITY TYPE: repository"
            )

            print(
                "========================================\n"
            )

            return repository

        # -------------------------------------------------
        # No entity
        # -------------------------------------------------

        print(
            "NO ENTITY FOUND"
        )

        print(
            "========================================\n"
        )

        return {
            "type": None,
            "name": None,
        }

    # =====================================================
    # Candidate Extraction
    # =====================================================

    @staticmethod
    def _extract_candidates(
        question: str,
    ) -> list[str]:
        """
        Extract possible repository identifiers from natural language.

        Supports:
        - Exact identifiers
        - Function calls
        - Qualified identifiers
        - Python filenames
        - Natural-language multi-word identifiers

        All candidates are only possibilities.
        Neo4j verifies whether they actually exist.
        """

        candidates: list[str] = []

        # -------------------------------------------------
        # 1. Backtick identifiers
        # -------------------------------------------------

        candidates.extend(
            re.findall(
                r"`([A-Za-z_][A-Za-z0-9_.-]*)`",
                question,
            )
        )

        # -------------------------------------------------
        # 2. Function calls
        # -------------------------------------------------

        candidates.extend(
            re.findall(
                r"\b"
                r"([A-Za-z_][A-Za-z0-9_]*"
                r"(?:\.[A-Za-z_][A-Za-z0-9_]*)*)"
                r"\s*\(",
                question,
            )
        )

        # -------------------------------------------------
        # 3. Qualified identifiers
        # -------------------------------------------------

        candidates.extend(
            re.findall(
                r"\b"
                r"[A-Za-z_][A-Za-z0-9_]*"
                r"(?:\.[A-Za-z_][A-Za-z0-9_]*)+"
                r"\b",
                question,
            )
        )

        # -------------------------------------------------
        # 4. Python filenames
        # -------------------------------------------------

        candidates.extend(
            re.findall(
                r"\b[A-Za-z0-9_.-]+\.py\b",
                question,
            )
        )

        # -------------------------------------------------
        # 5. Identifier-like words
        # -------------------------------------------------

        words = re.findall(
            r"\b[A-Za-z_][A-Za-z0-9_]*\b",
            question,
        )

        candidates.extend(words)

        # -------------------------------------------------
        # 6. Natural-language multi-word identifiers
        #
        # Example:
        #
        # "retrieval service"
        #       ↓
        # retrieval_service
        # RetrievalService
        #
        # "cross encoder reranker"
        #       ↓
        # cross_encoder_reranker
        # CrossEncoderReranker
        #
        # We generate possibilities only.
        # Neo4j still verifies them.
        # -------------------------------------------------

        for size in range(2, 5):

            for index in range(
                len(words) - size + 1
            ):

                group = words[
                    index:index + size
                ]

                # Skip groups containing very common
                # question words.
                if any(
                    word.lower()
                    in {
                        "what",
                        "which",
                        "where",
                        "when",
                        "why",
                        "how",
                        "does",
                        "do",
                        "is",
                        "are",
                        "the",
                        "this",
                        "that",
                        "these",
                        "those",
                        "and",
                        "or",
                        "of",
                        "to",
                        "for",
                        "from",
                        "with",
                        "my",
                        "your",
                    }
                    for word in group
                ):
                    continue

                snake_case = "_".join(
                    word.lower()
                    for word in group
                )

                pascal_case = "".join(
                    word[:1].upper()
                    + word[1:]
                    for word in group
                )

                candidates.append(
                    snake_case
                )

                candidates.append(
                    pascal_case
                )

        # -------------------------------------------------
        # 7. Normalize and remove duplicates
        # -------------------------------------------------

        unique_candidates: list[str] = []

        seen: set[str] = set()

        for candidate in candidates:

            candidate = candidate.strip()

            if not candidate:
                continue

            if candidate in seen:
                continue

            seen.add(candidate)

            unique_candidates.append(
                candidate
            )

        return unique_candidates

    # =====================================================
    # File Detection
    # =====================================================

    @staticmethod
    def _looks_like_file(
        candidate: str,
    ) -> bool:
        """
        Determine whether a candidate looks like a file name.

        This is syntax detection only.

        It does NOT assume that the file exists.
        Existence is verified through Neo4j.
        """

        return bool(
            re.fullmatch(
                r"[A-Za-z0-9_.-]+\.py",
                candidate,
                re.IGNORECASE,
            )
        )

    # =====================================================
    # Repository Resolution
    # =====================================================

    def _resolve_repository(
        self,
        question: str,
    ) -> dict | None:
        """
        Resolve repository-level questions.

        This does not depend on project-specific names.

        The graph itself determines whether a repository exists.
        """

        repository = self.graph.get_repository(
            repository_id=self.repository_id
        )

        if repository is None:
            return None

        # -------------------------------------------------
        # Repository-level intent
        #
        # We intentionally keep this generic.
        # -------------------------------------------------

        normalized = question.lower()

        repository_intent_patterns = (
            r"\brepository\b",
            r"\bproject\b",
            r"\bcodebase\b",
            r"\barchitecture\b",
            r"\bstructure\b",
            r"\boverview\b",
            r"\bwhole\s+(?:project|repository|codebase)\b",
            r"\bentire\s+(?:project|repository|codebase)\b",
        )

        for pattern in repository_intent_patterns:

            if re.search(
                pattern,
                normalized,
            ):

                repository_name = self._node_value(
                    repository,
                    "name",
                    "repository",
                )

                return {
                    "type": "repository",
                    "name": repository_name,
                }

        return None

    # =====================================================
    # Neo4j Node Helper
    # =====================================================

    @staticmethod
    def _node_value(
        node,
        key: str,
        default=None,
    ):
        """
        Safely read a property from a Neo4j Node or
        dictionary-like object.

        Supports both:

        Neo4j Node
        Dictionary
        """

        if node is None:
            return default

        # ---------------------------------------------
        # Dictionary
        # ---------------------------------------------

        if isinstance(
            node,
            dict,
        ):

            return node.get(
                key,
                default,
            )

        # ---------------------------------------------
        # Neo4j Node
        # ---------------------------------------------

        try:

            return node.get(
                key,
                default,
            )

        except AttributeError:

            pass

        # ---------------------------------------------
        # Generic object fallback
        # ---------------------------------------------

        return getattr(
            node,
            key,
            default,
        )