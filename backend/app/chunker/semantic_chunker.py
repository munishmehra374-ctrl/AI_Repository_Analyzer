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