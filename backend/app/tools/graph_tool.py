from app.knowledge.entity_resolver import EntityResolver
from app.knowledge.graph_queries import GraphQueries


class GraphTool:

    def __init__(
        self,
        graph_queries: GraphQueries,
    ):

        self.graph = graph_queries

        self.entity_resolver = EntityResolver(
            graph_queries
        )

    def execute(
        self,
        query: str,
    ) -> str:

        print("\n========== GRAPH TOOL ==========")
        print("Graph Query:", query)

        entity = self.entity_resolver.resolve(
            query
        )

        if entity["type"] == "function":

            return self._function_context(
                entity["name"]
            )

        elif entity["type"] == "class":

            return self._class_context(
                entity["name"]
            )

        elif entity["type"] == "file":

            return self._file_context(
                entity["name"]
            )

        elif entity["type"] == "repository":

            return self._repository_context()

        return "No graph information found."

    # =====================================================
    # Function
    # =====================================================

    def _function_context(
        self,
        qualified_name: str,
    ):

        if self.graph.get_function(
            qualified_name
        ) is None:

            return f"Function '{qualified_name}' not found."

        calls = self.graph.get_function_calls(
            qualified_name
        )

        called_by = self.graph.get_called_by(
            qualified_name
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
    # Class
    # =====================================================

    def _class_context(
        self,
        class_name: str,
    ):

        if self.graph.get_class(
            class_name
        ) is None:

            return f"Class '{class_name}' not found."

        methods = self.graph.get_class_methods(
            class_name
        )

        parents = self.graph.get_parent_classes(
            class_name
        )

        children = self.graph.get_child_classes(
            class_name
        )

        dependencies = self.graph.get_class_dependencies(
            class_name
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
"""

    # =====================================================
    # File
    # =====================================================

    def _file_context(
        self,
        file_path: str,
    ):

        classes = self.graph.get_file_classes(
            file_path
        )

        functions = self.graph.get_file_functions(
            file_path
        )

        imports = self.graph.get_imports(
            file_path
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
    # Repository
    # =====================================================

    def _repository_context(
        self,
    ):

        repository = self.graph.get_repository()

        structure = self.graph.get_repository_structure()

        lines = []

        if repository:

            lines.append(
                f"Repository: {repository['name']}"
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

        return "\n".join(lines)