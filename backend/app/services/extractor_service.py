from pathlib import Path

from app.parser.tree_sitter_parser import TreeSitterParser
from app.extractor.ast_extractor import ASTExtractor


class ExtractorService:

    def __init__(self):

        self.parser = TreeSitterParser()
        self.extractor = ASTExtractor()

    def extract(self, file_path: str):

        path = Path(file_path)

        source_code = path.read_text(
            encoding="utf-8"
        )

        tree = self.parser.parse(source_code)

        return self.extractor.extract(
            tree,
            source_code
        )