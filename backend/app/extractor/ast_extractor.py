from __future__ import annotations

from tree_sitter import Node

from app.extractor.import_extractor import ImportExtractor
from app.extractor.class_extractor import ClassExtractor
from app.extractor.function_extractor import FunctionExtractor


class ASTExtractor:
    """
    Coordinates extraction from the AST.
from __future__ import annotations

import uuid


class SemanticChunker:

    def chunk(
        self,
        extracted_data: dict,
        file_path: str,
        language: str,
    ):

        chunks = []

        # ---------------- Functions ---------------- #

        for function in extracted_data["functions"]:

            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "type": "function",
                    "name": function["name"],
                    "file_path": file_path,
                    "language": language,
                    "start_line": function["start_line"],
                    "end_line": function["end_line"],
                    "code": function["code"],
                }
            )

        # ---------------- Classes ---------------- #

        for cls in extracted_data["classes"]:

            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "type": "class",
                    "name": cls["name"],
                    "file_path": file_path,
                    "language": language,
                    "start_line": cls["start_line"],
                    "end_line": cls["end_line"],
                    "code": cls["code"],
                }
            )

        return chunks
    Responsibilities
    ----------------
    - Traverse the syntax tree.
    - Delegate extraction to specialized extractors.
    - Build a unified extraction result.
    """

    def __init__(self):

        self.import_extractor = ImportExtractor()

        self.class_extractor = ClassExtractor()

        self.function_extractor = FunctionExtractor()

    # =====================================================
    # Public API
    # =====================================================

    def extract(
        self,
        tree,
        source_code: str,
    ) -> dict:

        result = {

            "imports": [],

            "classes": [],

            "functions": [],

            # Future components
            "routes": [],

            "models": [],

            "dependencies": [],

            "inheritance": [],

            "file": {},
        }

        self._traverse(

            node=tree.root_node,

            source_code=source_code,

            result=result,

            current_class=None,

        )

        return result

    # =====================================================
    # AST Traversal
    # =====================================================

    def _traverse(
        self,
        node: Node,
        source_code: str,
        result: dict,
        current_class: str | None,
    ):

        # -------------------------------------------------
        # Import Statements
        # -------------------------------------------------

        if node.type in (

            "import_statement",

            "import_from_statement",

        ):

            result["imports"].append(

                self.import_extractor.extract(

                    node,

                    source_code,

                )

            )

            return

        # -------------------------------------------------
        # Class Definition
        # -------------------------------------------------

        if node.type == "class_definition":

            class_data = self.class_extractor.extract(

                node,

                source_code,

            )

            result["classes"].append(

                class_data

            )

            # Traverse inside the class
            for child in node.children:

                self._traverse(

                    child,

                    source_code,

                    result,

                    current_class=class_data["name"],

                )

            return
        # -------------------------------------------------
        # Function Definition
        # -------------------------------------------------

        if node.type in (

            "function_definition",

            "async_function_definition",

        ):

            function = self.function_extractor.extract(

                node,

                source_code,

                current_class,

            )

            result["functions"].append(

                function

            )

            return

        # -------------------------------------------------
        # Continue Traversal
        # -------------------------------------------------

        for child in node.children:

            self._traverse(

                child,

                source_code,

                result,

                current_class,

            )