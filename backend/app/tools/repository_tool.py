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
        print("Repository Query:", query)

        query = query.lower()

        # =====================================================
        # Repository Overview
        # =====================================================

        if any(keyword in query for keyword in [
            "summary",
            "overview",
            "repository",
            "project",
        ]):
            result = self.metadata.get_summary()

        # =====================================================
        # Architecture
        # =====================================================

        elif any(keyword in query for keyword in [
            "architecture",
            "design",
            "pipeline",
            "workflow",
            "indexing",
        ]):
            result = self.metadata.get_architecture()

        # =====================================================
        # Services
        # =====================================================

        elif any(keyword in query for keyword in [
            "service",
            "services",
        ]):
            result = self.metadata.get_services()

        # =====================================================
        # Routes
        # =====================================================

        elif any(keyword in query for keyword in [
            "route",
            "routes",
            "endpoint",
            "api",
        ]):
            result = self.metadata.get_routes()

        # =====================================================
        # Models
        # =====================================================

        elif any(keyword in query for keyword in [
            "model",
            "models",
        ]):
            result = self.metadata.get_models()

        # =====================================================
        # Statistics
        # =====================================================

        elif any(keyword in query for keyword in [
            "statistics",
            "stats",
            "count",
            "numbers",
        ]):
            result = self.metadata.get_statistics()

        # =====================================================
        # Modules
        # =====================================================

        elif any(keyword in query for keyword in [
            "module",
            "modules",
            "package",
            "packages",
        ]):
            result = self.metadata.get_modules()

        # =====================================================
        # Technologies
        # =====================================================

        elif any(keyword in query for keyword in [
            "framework",
            "frameworks",
            "technology",
            "technologies",
            "library",
            "libraries",
        ]):
            result = self.metadata.get_frameworks()

        # =====================================================
        # Dependencies
        # =====================================================

        elif any(keyword in query for keyword in [
            "dependency",
            "dependencies",
            "requirement",
            "requirements",
        ]):
            result = self.metadata.get_dependencies()

        # =====================================================
        # Languages
        # =====================================================

        elif any(keyword in query for keyword in [
            "language",
            "languages",
        ]):
            result = self.metadata.get_languages()

        # =====================================================
        # Default
        # =====================================================

        else:
            result = self.metadata.get_summary()

        print("\nRepository Tool Result:")
        print(result)
        print("=====================================\n")

        return result