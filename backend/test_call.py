from app.knowledge.models import (
    RepositoryGraph,
    FunctionNode,
)
from app.knowledge.relationship_builder import RelationshipBuilder


def main():

    print("=" * 70)
    print("TESTING FUNCTION CALL RESOLUTION")
    print("=" * 70)

    graph = RepositoryGraph()

    # ==========================================================
    # ChunkService.generate_chunks
    # ==========================================================

    graph.functions[
        "ChunkService.generate_chunks"
    ] = FunctionNode(
        qualified_name="ChunkService.generate_chunks",
        name="generate_chunks",
        file_path="app/services/chunk_service.py",
        class_name="ChunkService",
        is_method=True,
        is_async=False,
        visibility="public",
        is_static=False,
        is_classmethod=False,
        parameters=[],
        returns=None,

        calls=[
            {
                "type": "method",
                "object": "self.parser",
                "name": "parse",
                "full_name": "self.parser.parse",
            },
            {
                "type": "method",
                "object": "self",
                "name": "validate",
                "full_name": "self.validate",
            },
            {
                "type": "function",
                "object": None,
                "name": "unknown_function",
                "full_name": "unknown_function",
            },
        ],

        dependencies=[
            {
                "variable": "self.parser",
                "class": "TreeSitterParser",
            },
        ],

        decorators=[],
        start_line=1,
        end_line=20,
        code="",
    )

    # ==========================================================
    # Same-class method
    # ==========================================================

    graph.functions[
        "ChunkService.validate"
    ] = FunctionNode(
        qualified_name="ChunkService.validate",
        name="validate",
        file_path="app/services/chunk_service.py",
        class_name="ChunkService",
        is_method=True,
        is_async=False,
        visibility="public",
        is_static=False,
        is_classmethod=False,
        parameters=[],
        returns=None,
        calls=[],
        dependencies=[],
        decorators=[],
        start_line=21,
        end_line=30,
        code="",
    )

    # ==========================================================
    # Dependency target
    # ==========================================================

    graph.functions[
        "TreeSitterParser.parse"
    ] = FunctionNode(
        qualified_name="TreeSitterParser.parse",
        name="parse",
        file_path="app/parser/tree_sitter_parser.py",
        class_name="TreeSitterParser",
        is_method=True,
        is_async=False,
        visibility="public",
        is_static=False,
        is_classmethod=False,
        parameters=[],
        returns=None,
        calls=[],
        dependencies=[],
        decorators=[],
        start_line=1,
        end_line=10,
        code="",
    )

    # ==========================================================
    # Build relationships
    # ==========================================================

    print("\nFUNCTIONS IN GRAPH:")

    for name in graph.functions:
        print(" ", name)

    print("\n" + "=" * 70)
    print("RUNNING RELATIONSHIP BUILDER")
    print("=" * 70)

    builder = RelationshipBuilder()

    graph = builder.build(graph)

    # ==========================================================
    # Show CALL relationships
    # ==========================================================

    print("\n" + "=" * 70)
    print("CALL RELATIONSHIPS")
    print("=" * 70)

    call_relationships = [
        r
        for r in graph.relationships
        if r.relationship_type == "CALLS"
    ]

    for relationship in call_relationships:
        print(
            relationship.source,
            "->",
            relationship.target,
        )

    print(
        "\nTOTAL CALL RELATIONSHIPS:",
        len(call_relationships),
    )

    # ==========================================================
    # Expected
    # ==========================================================

    print("\n" + "=" * 70)
    print("EXPECTED")
    print("=" * 70)

    print(
        "ChunkService.generate_chunks -> "
        "TreeSitterParser.parse"
    )

    print(
        "ChunkService.generate_chunks -> "
        "ChunkService.validate"
    )

    print(
        "unknown_function should NOT be resolved"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()