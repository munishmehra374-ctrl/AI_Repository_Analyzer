from pathlib import Path

from app.parser.tree_sitter_parser import TreeSitterParser
from app.extractor.ast_extractor import ASTExtractor


class ExtractorService:

    def __init__(self):

        self.parser = TreeSitterParser()

        self.extractor = ASTExtractor()

    def extract(
        self,
        file_path: str,
    ) -> dict:

        path = Path(file_path)

        source_code = path.read_text(
            encoding="utf-8"
        )

        tree = self.parser.parse(
            source_code
        )

        extracted = self.extractor.extract(
            tree,
            source_code,
        )

        # ===========================================
        # Repository Metadata
        # ===========================================

        extracted["file_path"] = str(path)

        extracted["file_name"] = path.name

        extracted["folder_path"] = str(
            path.parent
        )

        extracted["repository_name"] = (
            path.parts[0]
            if len(path.parts) > 0
            else "repository"
        )

        extracted["repository_path"] = str(
            path.parents[-1]
            if len(path.parents) > 0
            else path.parent
        )

        extracted["language"] = (
            path.suffix.replace(".", "")
        )

        # ===========================================
        # Future Graph Components
        # ===========================================

        extracted.setdefault(
            "routes",
            [],
        )

        extracted.setdefault(
            "models",
            [],
        )

        extracted.setdefault(
            "dependencies",
            [],
        )

        extracted.setdefault(
            "inheritance",
            [],
        )

        extracted.setdefault(
            "imports",
            [],
        )

        extracted.setdefault(
            "classes",
            [],
        )

        extracted.setdefault(
            "functions",
            [],
        )

        return extracted