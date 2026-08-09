from __future__ import annotations

# =====================================================
# AI Repository Analyzer Architecture
# =====================================================

SYSTEM_SUMMARY = """
AI Repository Analyzer is a production-style repository understanding system
that indexes source code using AST extraction, semantic chunking, hybrid
retrieval (ChromaDB + BM25), a Neo4j Knowledge Graph and Repository Metadata.

The indexed repository can then be queried using a LangGraph-based workflow
consisting of a Planner, Tool Executor, Context Aggregator and Answer Generator.
"""

# =====================================================
# Indexing Pipeline
# =====================================================

INDEXING_PIPELINE = [

    "Repository Reader",

    "AST Extraction",

    "Semantic Chunking",

    "ChromaDB Vector Store",

    "BM25 Index",

    "Neo4j Knowledge Graph",

    "Repository Metadata",
]

# =====================================================
# Question Answering Pipeline
# =====================================================

QUESTION_ANSWERING_PIPELINE = [

    "Planner",

    "Tool Executor",

    "Context Aggregator",

    "Answer Generator",
]