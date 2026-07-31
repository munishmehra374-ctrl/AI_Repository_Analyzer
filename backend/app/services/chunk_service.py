from pathlib import Path

from app.parser.tree_sitter_parser import TreeSitterParser
from app.extractor.ast_extractor import ASTExtractor
from app.chunker.semantic_chunker import SemanticChunker


class ChunkService:

    def __init__(self):

        self.parser = TreeSitterParser()
        self.extractor = ASTExtractor()
        self.chunker = SemanticChunker()

    def generate_chunks(self, file_path: str):

        path = Path(file_path)

        source_code = path.read_text(
            encoding="utf-8"
        )

        tree = self.parser.parse(source_code)

        extracted_data = self.extractor.extract(
            tree,
            source_code
        )

        chunks = self.chunker.chunk(
            extracted_data=extracted_data,
            file_path=file_path,
            language="python"
        )

        return chunks