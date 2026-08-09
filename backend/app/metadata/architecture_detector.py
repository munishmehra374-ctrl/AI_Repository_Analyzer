from __future__ import annotations

from app.metadata.repository_metadata import RepositoryMetadata


class ArchitectureDetector:
    """
    Detects the overall repository architecture
    using repository profile information.

    Current Supported Architectures
    --------------------------------
    - Layered Architecture
    - RAG
    - Multi-Agent
    - Microservice (future)
    """

    def detect(
        self,
        metadata: RepositoryMetadata,
    ) -> str:

        modules = {
            module.lower()
            for module in metadata.modules
        }

        frameworks = {
            framework.lower()
            for framework in metadata.frameworks
        }

        llm_frameworks = {
            framework.lower()
            for framework in metadata.llm_frameworks
        }

        vector_databases = {
            db.lower()
            for db in metadata.vector_databases
        }

        databases = {
            db.lower()
            for db in metadata.databases
        }

        # ---------------------------------------
        # Multi-Agent
        # ---------------------------------------

        if (
            "langgraph" in llm_frameworks
            and (
                "agents" in modules
                or "planner" in modules
            )
        ):
            return "Multi-Agent Architecture"

        # ---------------------------------------
        # Retrieval-Augmented Generation
        # ---------------------------------------

        if (
            vector_databases
            and llm_frameworks
        ):
            return "Retrieval-Augmented Generation (RAG)"

        # ---------------------------------------
        # Layered Architecture
        # ---------------------------------------

        layered_modules = {
            "parser",
            "extractor",
            "services",
            "knowledge",
            "vectorstore",
            "retrieval",
        }

        if len(layered_modules & modules) >= 4:
            return "Layered Architecture"

        # ---------------------------------------
        # Web Backend
        # ---------------------------------------

        if (
            "fastapi" in frameworks
            or "flask" in frameworks
            or "django" in frameworks
        ):
            return "Web Backend"

        return "Unknown"