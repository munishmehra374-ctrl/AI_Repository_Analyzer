from app.knowledge.models import (
    RepositoryGraph,
    FunctionNode,
    ClassNode,
)
from app.knowledge.relationship_builder import RelationshipBuilder


# =====================================================
# Create a small fake graph
# =====================================================

graph = RepositoryGraph()

# -----------------------------------------------------
# Create dependency classes
# -----------------------------------------------------

hybrid = ClassNode(
    name="HybridRetriever",
    qualified_name="HybridRetriever",
    file_path="retrieval.py",
)

rrf = ClassNode(
    name="ReciprocalRankFusion",
    qualified_name="ReciprocalRankFusion",
    file_path="retrieval.py",
)

reranker = ClassNode(
    name="CrossEncoderReranker",
    qualified_name="CrossEncoderReranker",
    file_path="retrieval.py",
)

context = ClassNode(
    name="ContextOptimizer",
    qualified_name="ContextOptimizer",
    file_path="retrieval.py",
)

resolver = ClassNode(
    name="EntityResolver",
    qualified_name="EntityResolver",
    file_path="retrieval.py",
)


# -----------------------------------------------------
# Add classes to graph
# -----------------------------------------------------

graph.classes["HybridRetriever"] = hybrid
graph.classes["ReciprocalRankFusion"] = rrf
graph.classes["CrossEncoderReranker"] = reranker
graph.classes["ContextOptimizer"] = context
graph.classes["EntityResolver"] = resolver


# =====================================================
# Create RetrievalService function
# =====================================================

retrieval_init = FunctionNode(
    name="__init__",
    qualified_name="RetrievalService.__init__",
    class_name="RetrievalService",
    file_path="retrieval.py",
    dependencies=[
        {
            "variable": "hybrid_retriever",
            "class": "HybridRetriever",
        },
        {
            "variable": "rrf",
            "class": "ReciprocalRankFusion",
        },
        {
            "variable": "reranker",
            "class": "CrossEncoderReranker",
        },
        {
            "variable": "context_optimizer",
            "class": "ContextOptimizer",
        },
        {
            "variable": "entity_resolver",
            "class": "EntityResolver",
        },
    ],
    calls=[],
)


# -----------------------------------------------------
# Add function to graph
# -----------------------------------------------------

graph.functions[
    "RetrievalService.__init__"
] = retrieval_init


# =====================================================
# Run RelationshipBuilder
# =====================================================

builder = RelationshipBuilder()

graph = builder.build(graph)


# =====================================================
# Print results
# =====================================================

print()
print("========================================")
print("DEPENDS_ON TEST")
print("========================================")

for relationship in graph.relationships:

    if relationship.relationship_type == "DEPENDS_ON":

        print(
            relationship.source,
            "->",
            relationship.target,
        )

print("========================================")