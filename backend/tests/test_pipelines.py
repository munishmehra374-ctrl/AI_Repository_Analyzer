import unittest
from unittest.mock import MagicMock, patch
import json
import uuid


# =========================================================================
# Pipeline 1: Ingestion & AST Parsing Pipeline
# =========================================================================
class TestPipeline1IngestionAST(unittest.TestCase):
    def _create_mock_function(self, name, code, start_line=1, end_line=10, is_method=False):
        return {
            "name": name,
            "qualified_name": name,
            "class_name": "TestClass" if is_method else None,
            "is_method": is_method,
            "is_async": False,
            "visibility": "public",
            "is_static": False,
            "is_classmethod": False,
            "parameters": [],
            "returns": None,
            "decorators": [],
            "calls": [],
            "dependencies": [],
            "start_line": start_line,
            "end_line": end_line,
            "code": code
        }

    def test_semantic_chunker_functional_boundaries(self):
        from app.chunker.semantic_chunker import SemanticChunker

        chunker = SemanticChunker()
        mock_extracted = {
            "classes": [
                {
                    "name": "IndexingService",
                    "qualified_name": "IndexingService",
                    "visibility": "public",
                    "base_classes": [],
                    "decorators": [],
                    "start_line": 1,
                    "end_line": 50,
                    "code": "class IndexingService:\n    def __init__(self):\n        pass"
                }
            ],
            "functions": [
                self._create_mock_function("index_repository", "def index_repository(self):\n    pass", 10, 40, is_method=True)
            ]
        }

        chunks = chunker.chunk(mock_extracted, file_path="app/services/indexing_service.py", language="python")
        self.assertGreater(len(chunks), 0)
        func_chunks = [c for c in chunks if c["type"] == "function"]
        self.assertEqual(len(func_chunks), 1)
        self.assertEqual(func_chunks[0]["name"], "index_repository")
        self.assertEqual(func_chunks[0]["file_path"], "app/services/indexing_service.py")

    def test_semantic_chunker_oversized_code_splitting(self):
        from app.chunker.semantic_chunker import SemanticChunker

        chunker = SemanticChunker()
        large_code = "\n".join([f"    line_{i} = do_something({i})" for i in range(200)])
        mock_extracted = {
            "classes": [],
            "functions": [
                self._create_mock_function("huge_processing_pipeline", large_code, 1, 200, is_method=False)
            ]
        }

        chunks = chunker.chunk(mock_extracted, file_path="app/pipeline.py", language="python")
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertIn("line_", chunk["code"])


# =========================================================================
# Pipeline 2: Knowledge Graph Pipeline
# =========================================================================
class TestPipeline2KnowledgeGraph(unittest.TestCase):
    def test_multi_file_import_deduplication(self):
        from app.knowledge.graph_builder import GraphBuilder
        from app.knowledge.relationship_builder import RelationshipBuilder
        from app.knowledge.models import RepositoryGraph

        builder = GraphBuilder()
        graph = RepositoryGraph()

        extracted_file_a = {
            "file_path": "backend/app/api/repository.py",
            "imports": [{"statement": "from app.services.indexing_service import IndexingService"}],
            "classes": [],
            "functions": []
        }
        extracted_file_b = {
            "file_path": "backend/app/worker/indexing_tasks.py",
            "imports": [{"statement": "from app.services.indexing_service import IndexingService"}],
            "classes": [],
            "functions": []
        }

        builder._add_file_to_graph(graph, extracted_file_a)
        builder._add_file_to_graph(graph, extracted_file_b)

        self.assertEqual(len(graph.imports), 2)

        rel_builder = RelationshipBuilder()
        graph = rel_builder.build(graph)

        importers = {
            rel.source for rel in graph.relationships
            if rel.relationship_type == "IMPORTS"
        }
        self.assertIn("backend/app/api/repository.py", importers)
        self.assertIn("backend/app/worker/indexing_tasks.py", importers)

    def test_closed_world_zero_dependent_candidate_generation(self):
        from app.tools.graph_tool import GraphTool

        mock_gq = MagicMock()
        mock_gq.get_class.return_value = {"name": "IndexingService"}
        mock_gq.get_class_methods.return_value = ["index_repository"]
        mock_gq.get_parent_classes.return_value = []
        mock_gq.get_child_classes.return_value = []
        mock_gq.get_class_dependencies.return_value = ["GraphService"]
        mock_gq.get_dependent_classes.return_value = []

        tool = GraphTool(mock_gq, repository_id="test_repo")
        tool.entity_resolver = MagicMock()
        tool.entity_resolver.resolve.return_value = {"type": "class", "name": "IndexingService"}

        candidates = tool.get_candidates("What classes depend on IndexingService?")
        dependent_candidates = [c for c in candidates if c.get("category") == "dependent"]
        self.assertEqual(len(dependent_candidates), 1)
        self.assertIn("Dependent Classes:\nNone", dependent_candidates[0]["content"])


# =========================================================================
# Pipeline 3: Hybrid Retrieval & Ranking Pipeline
# =========================================================================
class TestPipeline3HybridRetrieval(unittest.TestCase):
    def test_bm25_exact_symbol_retrieval(self):
        from app.retrieval.bm25_index import BM25Index
        from app.retrieval.bm25_retriever import BM25Retriever

        index = BM25Index()
        chunks = [
            {"chunk_id": "1", "name": "index_repository", "code": "def index_repository(): pass"},
            {"chunk_id": "2", "name": "query_database", "code": "def query_database(): pass"},
            {"chunk_id": "3", "name": "unrelated_util", "code": "def calculate_sum(): pass"}
        ]
        index.build_index(chunks, repository_id="test_repo_123")

        retriever = BM25Retriever(index)
        results = retriever.retrieve("index_repository", repository_id="test_repo_123", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["chunk_id"], "1")

    def test_reciprocal_rank_fusion_score_aggregation(self):
        def rrf(rank_dense: int, rank_sparse: int, k: int = 60) -> float:
            return (1.0 / (k + rank_dense)) + (1.0 / (k + rank_sparse))

        top_item_score = rrf(1, 1)
        single_item_score = rrf(1, 50)
        self.assertGreater(top_item_score, single_item_score)
        self.assertAlmostEqual(rrf(1, 1, k=60), 2.0 / 61.0, places=5)


# =========================================================================
# Pipeline 4: Agentic RAG & LangGraph Orchestration Pipeline
# =========================================================================
class TestPipeline4AgenticOrchestration(unittest.TestCase):
    def test_repository_tool_intent_selection(self):
        from app.tools.repository_tool import RepositoryTool

        tool = RepositoryTool(metadata_service=MagicMock())
        profile = {
            "repository_id": "test_repo",
            "source_files": ["backend/app/main.py", "backend/app/services/indexing_service.py"],
            "summary": "Repository analyzer platform"
        }

        q1 = "Does this repository contain database.py?"
        res1 = tool._select_relevant_metadata(profile, q1)
        self.assertIn("source_files", res1)

        q2 = "Show repository profile"
        res2 = tool._select_relevant_metadata(profile, q2)
        self.assertNotIn("source_files", res2)

    def test_context_budget_trimming_and_grounding(self):
        from app.services.context_selection_service import ContextSelectionService

        service = ContextSelectionService()
        graph_cands = [
            {"name": "critical_graph_node", "content": "Critical AST Graph Context", "score": 1.0, "source": "graph"}
        ]
        retrieval_cands = [
            {"name": "large_code_chunk", "content": "def helper():\n" + "    pass\n" * 200, "score": 0.5, "source": "retrieval"}
        ]

        formatted = service.select_context(
            question="Explain indexing flow",
            retrieval_candidates=retrieval_cands,
            graph_candidates=graph_cands,
            repository_candidates=[],
            available_context_budget=400,
            requested_tools=["graph", "retrieval"]
        )

        self.assertIsInstance(formatted, str)
        self.assertIn("Critical AST Graph Context", formatted)


if __name__ == "__main__":
    unittest.main(verbosity=2)
