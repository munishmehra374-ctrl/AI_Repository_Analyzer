from app.knowledge.entity_resolver import EntityResolver
from app.knowledge.graph_queries import GraphQueries

import re


class GraphTool:

    def __init__(
        self,
        graph_queries: GraphQueries,
        repository_id: str,
    ):
        self.graph = graph_queries
        self.repository_id = repository_id

        self.entity_resolver = EntityResolver(
            graph_queries,
            repository_id=repository_id,
        )
    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        query: str,
    ) -> str:

        print(
            "\n========== GRAPH TOOL =========="
        )

        print(
            "Graph Query:",
            query
        )

        entity = self.entity_resolver.resolve(
            query
        )

        print(
            "Resolved Entity:"
        )

        print(
            entity
        )

        # =====================================================
        # Files Importing File
        # =====================================================

        query_lower = query.lower()

        if (
            "which files import" in query_lower
            or "what files import" in query_lower
            or "which file imports" in query_lower
            or "who imports" in query_lower
            or "depend on" in query_lower
            or "depends on" in query_lower
            or "dependent on" in query_lower
            or "depending on" in query_lower
        ):

            if (
                entity
                and entity["type"] == "file"
            ):

                return (
                    self._files_importing_context(
                        entity["name"]
                    )
                )

        if entity is None:

            print(
                "No entity resolved."
            )

            return (
                "No graph information found."
            )

        print(
            "Entity Type:",
            entity["type"]
        )

        if entity["type"] == "function":

            return (
                self._function_context(
                    entity["name"]
                )
            )

        elif entity["type"] == "class":

            return (
                self._class_context(
                    entity["name"]
                )
            )

        elif entity["type"] == "file":

            return (
                self._file_context(
                    entity["name"]
                )
            )

        elif entity["type"] == "repository":

            return (
                self._repository_context()
            )

        return (
            "No graph information found."
        )

    # =====================================================
    # Detect requested function relationship
    # =====================================================

    @staticmethod
    def _get_function_relationship(
        query: str,
    ) -> str:

        query = query.lower().strip()

        # Caller / Called By questions
        caller_phrases = (
            "which functions call",
            "what functions call",
            "which function calls",
            "what function calls",
            "who calls",
            "who is calling",
            "which methods call",
            "what methods call",
            "which method calls",
            "what method calls",
            "called by",
        )

        if any(
            phrase in query
            for phrase in caller_phrases
        ):
            return "called_by"

        # Callee / Calls questions
        callee_phrases = (
            "which functions does",
            "what functions does",
            "which functions did",
            "what functions did",
            "which methods does",
            "what methods does",
            "which method does",
            "what method does",
            "what does",
            "what did",
            "calls",
        )

        if any(
            phrase in query
            for phrase in callee_phrases
        ):
            return "calls"

        # No clear direction.
        # Preserve current behavior.
        return "both"

    # =====================================================
    # GLOBAL SELECTION CANDIDATES
    # =====================================================

    def get_candidates(
        self,
        query: str,
        question_type: str | None = None,
        repository_id: str | None = None,
    ) -> list[dict]:

        print(
            "\n========== GRAPH CANDIDATES =========="
        )

        print(
            "Query:",
            query,
        )

        print(
            "Question type:",
            question_type,
        )

        print(
            "Repository ID:",
            repository_id,
        )

        # =====================================================
        # Entity Resolution
        # =====================================================

        entity = self.entity_resolver.resolve(
            query
        )

        print(
            "Resolved entity:",
            entity,
        )

        # =====================================================
        # Repository Flow Questions
        # =====================================================

        entity_unresolved = (
            entity is None
            or entity.get("type") is None
            or entity.get("name") is None
        )

        if entity_unresolved:

            print(
                "No entity resolved."
            )

            print(
                "Question type:",
                question_type,
            )

            if question_type == "flow":

                print(
                    "Flow question detected."
                )

                print(
                    "Calling _get_flow_candidates()."
                )

                flow_candidates = (
                    self._get_flow_candidates(
                        query=query,
                        repository_id=repository_id,
                    )
                )

                print(
                    "Flow candidates returned:",
                    len(flow_candidates),
                )

                return flow_candidates

            print(
                "Not a flow question."
            )

            print(
                "Returning empty graph candidates."
            )

            return []
        # =====================================================
        # Entity Information
        # =====================================================

        entity_type = entity["type"]

        entity_name = entity["name"]

        candidates = []

        print(
            "Entity Type:",
            entity_type,
        )

        print(
            "Entity Name:",
            entity_name,
        )

        # =====================================================
        # Function
        # =====================================================

        if entity_type == "function":

            if (
                self.graph.get_function(
                    entity_name,
                    repository_id=self.repository_id,
                )
                is None
            ):

                return []

            relationship = (
                self._get_function_relationship(
                    query
                )
            )

            print(
                "Requested relationship:",
                relationship,
            )

            calls = []

            called_by = []

            if relationship in (
                "calls",
                "both",
            ):

                calls = (
                    self.graph.get_function_calls(
                        entity_name,
                        repository_id=self.repository_id,
                    )
                )

            if relationship in (
                "called_by",
                "both",
            ):

                called_by = (
                    self.graph.get_called_by(
                        entity_name,
                        repository_id=self.repository_id,
                    )
                )

            candidates.append(
                {
                    "source": "graph",
                    "type": "function",
                    "category": "entity",
                    "name": entity_name,
                    "qualified_name": entity_name,
                    "content": (
                        f"Function:\n"
                        f"{entity_name}"
                    ),
                    "rank": 0,
                }
            )

            for index, function in enumerate(
                calls
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "calls",
                        "name": function,
                        "qualified_name": (
                            f"{entity_name}.{function}"
                        ),
                        "content": (
                            f"Function:\n"
                            f"{entity_name}\n\n"
                            f"Calls:\n"
                            f"{function}"
                        ),
                        "rank": index + 1,
                    }
                )

            for index, function in enumerate(
                called_by
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "called_by",
                        "name": function,
                        "qualified_name": function,
                        "content": (
                            f"Function:\n"
                            f"{entity_name}\n\n"
                            f"Called By:\n"
                            f"{function}"
                        ),
                        "rank": index + 1,
                    }
                )

        # =====================================================
        # Class
        # =====================================================

        elif entity_type == "class":

            if (
                self.graph.get_class(
                    entity_name,
                    repository_id=self.repository_id,
                )
                is None
            ):

                return []

            methods = (
                self.graph.get_class_methods(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            parents = (
                self.graph.get_parent_classes(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            children = (
                self.graph.get_child_classes(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            dependencies = (
                self.graph.get_class_dependencies(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            dependent_classes = (
                self.graph.get_dependent_classes(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            candidates.append(
                {
                    "source": "graph",
                    "type": "class",
                    "category": "entity",
                    "name": entity_name,
                    "qualified_name": entity_name,
                    "content": (
                        f"Class:\n"
                        f"{entity_name}"
                    ),
                    "rank": 0,
                }
            )

            for index, method in enumerate(
                methods
            ):

                qualified_method = (
                    f"{entity_name}.{method}"
                )

                calls = (
                    self.graph.get_function_calls(
                        qualified_method,
                        repository_id=self.repository_id,
                    )
                )

                called_by = (
                    self.graph.get_called_by(
                        qualified_method,
                        repository_id=self.repository_id,
                    )
                )

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "method",
                        "name": method,
                        "qualified_name": (
                            qualified_method
                        ),
                        "content": (
                            f"Class:\n"
                            f"{entity_name}\n\n"
                            f"Method:\n"
                            f"{method}\n\n"
                            f"Calls:\n"
                            f"{', '.join(calls) if calls else 'None'}\n\n"
                            f"Called By:\n"
                            f"{', '.join(called_by) if called_by else 'None'}"
                        ),
                        "rank": index + 1,
                    }
                )

            for index, parent in enumerate(
                parents
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "parent",
                        "name": parent,
                        "qualified_name": parent,
                        "content": (
                            f"Class:\n"
                            f"{entity_name}\n\n"
                            f"Parent Class:\n"
                            f"{parent}"
                        ),
                        "rank": index + 1,
                    }
                )

            for index, child in enumerate(
                children
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "child",
                        "name": child,
                        "qualified_name": child,
                        "content": (
                            f"Class:\n"
                            f"{entity_name}\n\n"
                            f"Child Class:\n"
                            f"{child}"
                        ),
                        "rank": index + 1,
                    }
                )

            if not dependencies:
                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "dependency",
                        "name": "None",
                        "qualified_name": "None",
                        "content": (
                            f"Class:\n"
                            f"{entity_name}\n\n"
                            f"Dependencies:\n"
                            f"None"
                        ),
                        "rank": 1,
                    }
                )

            for index, dependency in enumerate(
                dependencies
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "dependency",
                        "name": dependency,
                        "qualified_name": dependency,
                        "content": (
                            f"Class:\n"
                            f"{entity_name}\n\n"
                            f"Dependency:\n"
                            f"{dependency}"
                        ),
                        "rank": index + 1,
                    }
                )

            if not dependent_classes:
                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "dependent",
                        "name": "None",
                        "qualified_name": "None",
                        "content": (
                            f"Class:\n"
                            f"{entity_name}\n\n"
                            f"Dependent Classes:\n"
                            f"None"
                        ),
                        "rank": 1,
                    }
                )

            for index, dependent in enumerate(
                dependent_classes
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "dependent",
                        "name": dependent,
                        "qualified_name": dependent,
                        "content": (
                            f"Class:\n"
                            f"{entity_name}\n\n"
                            f"Dependent Class:\n"
                            f"{dependent}"
                        ),
                        "rank": index + 1,
                    }
                )

        # =====================================================
        # File
        # =====================================================

        elif entity_type == "file":

            classes = (
                self.graph.get_file_classes(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            functions = (
                self.graph.get_file_functions(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            imports = (
                self.graph.get_imports(
                    entity_name,
                    repository_id=self.repository_id,
                )
            )

            candidates.append(
                {
                    "source": "graph",
                    "type": "file",
                    "category": "entity",
                    "name": entity_name,
                    "qualified_name": entity_name,
                    "content": (
                        f"File:\n"
                        f"{entity_name}"
                    ),
                    "rank": 0,
                }
            )

            for index, class_name in enumerate(
                classes
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "class",
                        "name": class_name,
                        "qualified_name": class_name,
                        "content": (
                            f"File:\n"
                            f"{entity_name}\n\n"
                            f"Class:\n"
                            f"{class_name}"
                        ),
                        "rank": index + 1,
                    }
                )

            for index, function in enumerate(
                functions
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "function",
                        "name": function,
                        "qualified_name": function,
                        "content": (
                            f"File:\n"
                            f"{entity_name}\n\n"
                            f"Function:\n"
                            f"{function}"
                        ),
                        "rank": index + 1,
                    }
                )

            for index, import_statement in enumerate(
                imports
            ):

                candidates.append(
                    {
                        "source": "graph",
                        "type": "relationship",
                        "category": "import",
                        "name": import_statement,
                        "qualified_name": import_statement,
                        "content": (
                            f"File:\n"
                            f"{entity_name}\n\n"
                            f"Import:\n"
                            f"{import_statement}"
                        ),
                        "rank": index + 1,
                    }
                )

        # =====================================================
        # Files Importing File
        # =====================================================

        query_lower = query.lower()

        if (
            "which files import" in query_lower
            or "what files import" in query_lower
            or "which file imports" in query_lower
            or "who imports" in query_lower
            or "depend on" in query_lower
            or "depends on" in query_lower
            or "dependent on" in query_lower
            or "depending on" in query_lower
        ):

            if entity_type == "file":

                files = (
                    self.graph.get_files_importing(
                        entity_name,
                        repository_id=self.repository_id,
                    )
                )

                candidates = []

                if not files:

                    candidates.append(
                        {
                            "source": "graph",
                            "type": "relationship",
                            "category": "imported_by",
                            "name": "None",
                            "qualified_name": "None",
                            "content": (
                                f"File:\n"
                                f"{entity_name}\n\n"
                                f"Imported By:\n"
                                f"None"
                            ),
                            "rank": 0,
                        }
                    )

                else:

                    for index, file in enumerate(
                        files
                    ):

                        candidates.append(
                            {
                                "source": "graph",
                                "type": "relationship",
                                "category": "imported_by",
                                "name": file,
                                "qualified_name": file,
                                "content": (
                                    f"File:\n"
                                    f"{entity_name}\n\n"
                                    f"Imported By:\n"
                                    f"{file}"
                                ),
                                "rank": index,
                            }
                        )

        # =====================================================
        # Repository
        # =====================================================

        elif entity_type == "repository":

            repository = (
                self.graph.get_repository()
            )

            structure = (
                self.graph.get_repository_structure()
            )

            if repository:

                candidates.append(
                    {
                        "source": "graph",
                        "type": "repository",
                        "category": "entity",
                        "name": repository["name"],
                        "qualified_name": repository["name"],
                        "content": (
                            f"Repository:\n"
                            f"{repository['name']}"
                        ),
                        "rank": 0,
                    }
                )

            for index, folder in enumerate(
                structure
            ):

                files = folder.get(
                    "files",
                    [],
                )

                candidates.append(
                    {
                        "source": "graph",
                        "type": "repository_structure",
                        "category": "folder",
                        "name": folder["folder"],
                        "qualified_name": folder["folder"],
                        "content": (
                            f"Folder:\n"
                            f"{folder['folder']}\n\n"
                            f"Files:\n"
                            f"{', '.join(files)}"
                        ),
                        "rank": index + 1,
                    }
                )

        # =====================================================
        # Final Diagnostics
        # =====================================================

        print(
            "Graph candidates:",
            len(candidates),
        )

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            print(
                f"\nGraph Candidate {index}"
            )

            print(
                "Name:",
                candidate.get("name"),
            )

            print(
                "Qualified:",
                candidate.get(
                    "qualified_name"
                ),
            )

            print(
                "Category:",
                candidate.get(
                    "category"
                ),
            )

        print(
            "======================================\n"
        )

        return candidates

    # =====================================================
    # Repository Flow Candidates
    # =====================================================

    def _get_flow_candidates(
        self,
        query: str,
        repository_id: str | None,
    ) -> list[dict]:

        print(
            "\n========== GRAPH FLOW CANDIDATES =========="
        )

        if not repository_id:
            print(
                "No repository ID available."
            )
            return []

        relationships = (
            self.graph.get_dependency_graph(
                repository_id
            )
        )

        print(
            "Dependency relationships:",
            len(relationships),
        )

        # =====================================================
        # Query terms
        # =====================================================

        query_terms = set(
            re.findall(
                r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
                query.lower(),
            )
        )

        stop_words = {
            "how",
            "does",
            "what",
            "which",
            "why",
            "where",
            "when",
            "the",
            "a",
            "an",
            "is",
            "are",
            "to",
            "from",
            "through",
            "and",
            "or",
            "of",
            "in",
            "on",
            "for",
            "with",
            "this",
            "that",
            "user",
            "question",
            "components",
            "involved",
            "interact",
        }

        query_terms -= stop_words

        # =====================================================
        # Score relationships
        # =====================================================

        scored_relationships = []

        for relationship in relationships:

            source = relationship.get(
                "source"
            )

            target = relationship.get(
                "target"
            )

            relationship_type = relationship.get(
                "relationship"
            )

            source_type = relationship.get(
                "source_type"
            )

            target_type = relationship.get(
                "target_type"
            )

            if not source or not target:
                continue

            text = " ".join(
                [
                    str(source),
                    str(target),
                    str(relationship_type or ""),
                    str(source_type or ""),
                    str(target_type or ""),
                ]
            ).lower()

            relationship_terms = set(
                re.findall(
                    r"\b[a-zA-Z_][a-zA-Z0-9_]*\b",
                    text,
                )
            )

            # -------------------------------------------------
            # Lexical relevance
            # -------------------------------------------------

            overlap = (
                query_terms
                & relationship_terms
            )

            score = len(overlap)

            scored_relationships.append(
                (
                    score,
                    relationship,
                )
            )

        # =====================================================
        # Sort by relevance
        # =====================================================

        scored_relationships.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        # =====================================================
        # Keep a bounded number
        # =====================================================

        MAX_FLOW_CANDIDATES = 40

        selected_relationships = (
            scored_relationships[
                :MAX_FLOW_CANDIDATES
            ]
        )

        candidates: list[dict] = []

        # =====================================================
        # Build candidates
        # =====================================================

        for rank, (
            score,
            relationship,
        ) in enumerate(
            selected_relationships,
            start=1,
        ):

            source = relationship.get(
                "source"
            )

            target = relationship.get(
                "target"
            )

            relationship_type = relationship.get(
                "relationship"
            )

            source_type = relationship.get(
                "source_type"
            )

            target_type = relationship.get(
                "target_type"
            )

            content = (
                f"Source: {source}\n"
                f"Source Type: {source_type}\n"
                f"Relationship: {relationship_type}\n"
                f"Target: {target}\n"
                f"Target Type: {target_type}"
            )

            candidates.append(
                {
                    "source": "graph",
                    "type": "relationship",
                    "category": "flow",
                    "name": source,
                    "qualified_name": (
                        f"{source} -> {target}"
                    ),
                    "content": content,
                    "rank": rank,
                    "graph_relevance_score": score,
                }
            )

        # =====================================================
        # Diagnostics
        # =====================================================

        print(
            "Graph flow candidates:",
            len(candidates),
        )

        print(
            "\n---------- SELECTED FLOW RELATIONSHIPS ----------"
        )

        for index, candidate in enumerate(
            candidates,
            start=1,
        ):

            print(
                f"{index}.",
                candidate.get(
                    "qualified_name"
                ),
                "| score:",
                candidate.get(
                    "graph_relevance_score"
                ),
            )

        print(
            "===========================================\n"
        )

        return candidates
    
    # =====================================================
    # Function Context
    # =====================================================

    def _function_context(
        self,
        qualified_name: str,
    ):

        if (
            self.graph.get_function(
                qualified_name,
                repository_id=self.repository_id,
            ) is None
        ):

            return (
                f"Function "
                f"'{qualified_name}' "
                f"not found."
            )

        calls = (
            self.graph.get_function_calls(
                qualified_name,
                repository_id=self.repository_id,
            )
        )

        called_by = (
            self.graph.get_called_by(
                qualified_name,
                repository_id=self.repository_id,
            )
        )

        return f"""
Function:
{qualified_name}

Calls:
{", ".join(calls) if calls else "None"}

Called By:
{", ".join(called_by) if called_by else "None"}
"""

    # =====================================================
    # Class Context
    # =====================================================

    def _class_context(
        self,
        class_name: str,
    ):

        if (
            self.graph.get_class(
                class_name,
                repository_id=self.repository_id,
            ) is None
        ):

            return (
                f"Class "
                f"'{class_name}' "
                f"not found."
            )

        methods = (
            self.graph.get_class_methods(
                class_name,
                repository_id=self.repository_id,
            )
        )

        parents = (
            self.graph.get_parent_classes(
                class_name,
                repository_id=self.repository_id,
            )
        )

        children = (
            self.graph.get_child_classes(
                class_name,
                repository_id=self.repository_id,
            )
        )

        dependencies = (
            self.graph.get_class_dependencies(
                class_name,
                repository_id=self.repository_id,
            )
        )

        dependent_classes = (
            self.graph.get_dependent_classes(
                class_name,
                repository_id=self.repository_id,
            )
        )

        return f"""
Class:
{class_name}

Methods:
{", ".join(methods) if methods else "None"}

Parent Classes:
{", ".join(parents) if parents else "None"}

Child Classes:
{", ".join(children) if children else "None"}

Dependencies:
{", ".join(dependencies) if dependencies else "None"}

Dependent Classes:
{", ".join(dependent_classes) if dependent_classes else "None"}
"""

    # =====================================================
    # File Context
    # =====================================================

    def _file_context(
        self,
        file_path: str,
    ):

        classes = (
            self.graph.get_file_classes(
                file_path,
                repository_id=self.repository_id,
            )
        )

        functions = (
            self.graph.get_file_functions(
                file_path,
                repository_id=self.repository_id,
            )
        )

        imports = (
            self.graph.get_imports(
                file_path,
                repository_id=self.repository_id,
            )
        )

        return f"""
File:
{file_path}

Classes:
{", ".join(classes) if classes else "None"}

Functions:
{", ".join(functions) if functions else "None"}

Imports:
{", ".join(imports) if imports else "None"}
"""

    # =====================================================
    # Files Importing File
    # =====================================================

    def _files_importing_context(
        self,
        file_name: str,
    ):

        files = (
            self.graph.get_files_importing(
                file_name,
                repository_id=self.repository_id,
            )
        )

        return f"""
File:
{file_name}

Imported By:
{", ".join(files) if files else "None"}
"""

    # =====================================================
    # Repository Context
    # =====================================================

    def _repository_context(
        self,
    ):

        repository = (
            self.graph.get_repository()
        )

        structure = (
            self.graph.get_repository_structure()
        )

        lines = []

        if repository:

            lines.append(
                f"Repository: "
                f"{repository['name']}"
            )

        lines.append("")
        lines.append("Structure:")

        for folder in structure:

            lines.append(
                f"\n{folder['folder']}"
            )

            for file in folder["files"]:

                if file:

                    lines.append(
                        f"  └── {file}"
                    )

        return "\n".join(
            lines
        )