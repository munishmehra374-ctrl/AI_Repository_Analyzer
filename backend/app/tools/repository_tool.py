from app.services.repository_metadata_service import RepositoryMetadataService


class RepositoryTool:

    def __init__(
        self,
        metadata_service: RepositoryMetadataService,
    ):

        self.metadata = metadata_service

    def execute(
        self,
        query: str,
    ):

        print("\n========== REPOSITORY TOOL ==========")
        print("Question:", query)

        query = query.lower()

        if "summary" in query or "overview" in query:
            result = self.metadata.get_summary()

        elif "architecture" in query:
            result = self.metadata.get_architecture()

        elif "service" in query:
            result = self.metadata.get_services()

        elif "route" in query or "endpoint" in query:
            result = self.metadata.get_routes()

        elif "model" in query:
            result = self.metadata.get_models()

        elif "statistics" in query or "stats" in query:
            result = self.metadata.get_statistics()

        else:
            result = self.metadata.get_summary()

        print("\nRepository Tool Result:")
        print(result)
        print("=====================================\n")

        return result