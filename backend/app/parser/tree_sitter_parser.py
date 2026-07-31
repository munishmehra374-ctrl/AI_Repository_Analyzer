from tree_sitter import Language, Parser
import tree_sitter_python


class TreeSitterParser:

    def __init__(self):
        self.parser = Parser()
        self.python_language = Language(tree_sitter_python.language())

    def parse(self, source_code: str):
        self.parser.language = self.python_language

        tree = self.parser.parse(source_code.encode("utf-8"))

        return tree