from __future__ import annotations

from tree_sitter import Node


class ImportExtractor:
    """
    Extracts Python import statements.

    Supported
    ---------

    import os

    import numpy as np

    import chromadb

    from fastapi import FastAPI

    from app.services import RetrievalService
    """

    def extract(
        self,
        node: Node,
        source_code: str,
    ) -> dict:

        statement = source_code[
            node.start_byte:node.end_byte
        ]

        result = {

            # Original statement
            "statement": statement,

            # import / from
            "type": None,

            # fastapi
            "module": None,

            # ["FastAPI"]
            "imported_names": [],

            # np
            "alias": None,
        }

        # ==========================================
        # import xxx
        # ==========================================

        if node.type == "import_statement":

            result["type"] = "import"

            for child in node.children:

                text = source_code[
                    child.start_byte:
                    child.end_byte
                ]

                if child.type == "dotted_name":

                    result["module"] = text

                    result["imported_names"].append(text)

                elif child.type == "aliased_import":

                    for grandchild in child.children:

                        value = source_code[
                            grandchild.start_byte:
                            grandchild.end_byte
                        ]

                        if grandchild.type == "dotted_name":

                            result["module"] = value

                            result["imported_names"].append(value)

                        elif grandchild.type == "identifier":

                            result["alias"] = value

        # ==========================================
        # from xxx import yyy
        # ==========================================

        elif node.type == "import_from_statement":

            result["type"] = "from"

            module_found = False

            for child in node.children:

                text = source_code[
                    child.start_byte:
                    child.end_byte
                ]

                if child.type == "dotted_name" and not module_found:

                    result["module"] = text

                    module_found = True

                elif child.type == "dotted_name" and module_found:

                    result["imported_names"].append(text)

                elif child.type == "identifier" and module_found:

                    result["imported_names"].append(text)

        return result