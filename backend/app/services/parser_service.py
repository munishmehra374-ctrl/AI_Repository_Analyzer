from pathlib import Path

from app.parser.tree_sitter_parser import TreeSitterParser


class ParserService:

    def __init__(self):
        self.parser = TreeSitterParser()

    def parse_file(self, file_path: str):

        path = Path(file_path)

        source_code = path.read_text(encoding="utf-8")

        tree = self.parser.parse(source_code)

        return tree