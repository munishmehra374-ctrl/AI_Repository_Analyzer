from app.knowledge.graph_builder import GraphBuilder
from app.knowledge.neo4j_store import Neo4jStore


class GraphService:

    def __init__(self):

        self.builder = GraphBuilder()
        self.neo4j = Neo4jStore()

    def build_graph(self, extracted_data: dict):

        graph = self.builder.build(extracted_data)

        self.neo4j.store_graph(graph)

        return graph