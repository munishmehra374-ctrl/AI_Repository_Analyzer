from __future__ import annotations

import uuid


class SemanticChunker:

    MAX_CHARS_PER_CHUNK = 2000  # Approximately 500 tokens

    def _split_large_code(self, code: str, max_chars: int = 2000) -> list[str]:
        """Splits oversized code blocks into sub-chunks of ~500 tokens."""
        if len(code) <= max_chars:
            return [code]

        lines = code.split("\n")
        sub_chunks = []
        current_chunk = []
        current_len = 0

        for line in lines:
            line_len = len(line) + 1  # include newline
            if current_len + line_len > max_chars and current_chunk:
                sub_chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_len = line_len
            else:
                current_chunk.append(line)
                current_len += line_len

        if current_chunk:
            sub_chunks.append("\n".join(current_chunk))

        return sub_chunks

    def chunk(
        self,
        extracted_data: dict,
        file_path: str,
        language: str,
    ):
        chunks = []

        # =====================================================
        # 1. Functions & Methods (Capped at ~500 tokens)
        # =====================================================
        for function in extracted_data.get("functions", []):
            code_body = function["code"]
            code_parts = self._split_large_code(code_body, self.MAX_CHARS_PER_CHUNK)

            for idx, part in enumerate(code_parts):
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
                        "part_index": idx,
                        "total_parts": len(code_parts),
                        "code": part,
                    }
                )

        # =====================================================
        # 2. Classes (Store Skeletons / Headers, NOT Full Bodies)
        # =====================================================
        for cls in extracted_data.get("classes", []):
            # Instead of storing the full monolithic body (which can be 30k+ tokens),
            # we create a class definition header. Method logic is already covered by function chunks above.
            raw_code = cls["code"]
            class_lines = raw_code.split("\n")
            
            # Extract header lines (e.g. class ClassName(Base): and docstring/init signature)
            header_lines = [line for line in class_lines if line.strip().startswith(("class ", "def __init__", "def ", "@")) or not line.strip()]
            skeleton_code = "\n".join(header_lines[:30]) # Take top 30 structural lines

            chunks.append(
                {
                    "chunk_id": str(uuid.uuid4()),
                    "type": "class_skeleton",
                    "name": cls["name"],
                    "qualified_name": cls["qualified_name"],
                    "file_path": file_path,
                    "language": language,
                    "visibility": cls["visibility"],
                    "base_classes": cls["base_classes"],
                    "decorators": cls["decorators"],
                    "start_line": cls["start_line"],
                    "end_line": cls["end_line"],
                    "code": skeleton_code if skeleton_code.strip() else raw_code[:1500],
                }
            )

        return chunks