from tree_sitter import Node


class ASTExtractor:

    def extract(self, tree, source_code: str):

        root = tree.root_node

        result = {
            "imports": [],
            "functions": [],
            "classes": []
        }

        self._traverse(root, source_code, result)

        return result

    def _traverse(self, node: Node, source_code: str, result):

        if node.type == "import_statement":
            result["imports"].append(
                source_code[node.start_byte:node.end_byte]
            )

        elif node.type == "import_from_statement":
            result["imports"].append(
                source_code[node.start_byte:node.end_byte]
            )

        elif node.type == "function_definition":

            function = self._extract_function(node, source_code)

            result["functions"].append(function)

        elif node.type == "class_definition":

            cls = self._extract_class(node, source_code)

            result["classes"].append(cls)

        for child in node.children:
            self._traverse(child, source_code, result)

    def _extract_function(self, node: Node, source_code: str):

        function_name = ""

        for child in node.children:

            if child.type == "identifier":
                function_name = source_code[
                    child.start_byte:child.end_byte
                ]
                break

        return {
            "name": function_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code": source_code[node.start_byte:node.end_byte]
        }

    def _extract_class(self, node: Node, source_code: str):

        class_name = ""

        for child in node.children:

            if child.type == "identifier":
                class_name = source_code[
                    child.start_byte:child.end_byte
                ]
                break

        return {
            "name": class_name,
            "start_line": node.start_point[0] + 1,
            "end_line": node.end_point[0] + 1,
            "code": source_code[node.start_byte:node.end_byte]
        }