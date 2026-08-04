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

        print(f"\nProcessing: {file_path}")
        print(f"Source code length: {len(source_code)}")

        tree = self.parser.parse(source_code)

        print("Tree parsed successfully.")

        extracted_data = self.extractor.extract(
            tree,
            source_code
        )

        print("Extracted data:")
        print(type(extracted_data))
        print(extracted_data)

        chunks = self.chunker.chunk(
            extracted_data=extracted_data,
            file_path=file_path,
            language="python"
        )

        print(f"Chunks generated: {len(chunks)}")

        return {
            "chunks": chunks,
            "ast": extracted_data,
            "source_code": source_code
        }