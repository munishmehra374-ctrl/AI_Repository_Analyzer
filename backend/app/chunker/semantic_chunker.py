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

        # =====================================================
        # Functions
        # =====================================================

        for function in extracted_data["functions"]:

            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),

                    "type": "function",

                    "name": function["name"],

                    "qualified_name": function["qualified_name"],

                    "class_name": function["class_name"],

                    "file_path": file_path,

                    "language": language,

                    "is_method": function["is_method"],

                    "is_async": function["is_async"],

                    "visibility": function["visibility"],

                    "is_static": function["is_static"],

                    "is_classmethod": function["is_classmethod"],

                    "parameters": function["parameters"],

                    "returns": function["returns"],

                    "decorators": function["decorators"],

                    "calls": function["calls"],

                    "dependencies": function["dependencies"],

                    "start_line": function["start_line"],

                    "end_line": function["end_line"],

                    "code": function["code"],
                }
            )

        # =====================================================
        # Classes
        # =====================================================

        for cls in extracted_data["classes"]:

            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),

                    "type": "class",

                    "name": cls["name"],

                    "qualified_name": cls["qualified_name"],

                    "file_path": file_path,

                    "language": language,

                    "visibility": cls["visibility"],

                    "base_classes": cls["base_classes"],

                    "decorators": cls["decorators"],

                    "start_line": cls["start_line"],

                    "end_line": cls["end_line"],

                    "code": cls["code"],
                }
            )

        return chunks