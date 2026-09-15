import json
import re

from app.core.redis import redis_client
from app.services.repository_metadata_service import (
    RepositoryMetadataService,
)


class RepositoryTool:

    def __init__(
        self,
        metadata_service: RepositoryMetadataService,
    ):

        self.metadata = metadata_service

    # =====================================================
    # Load Repository Profile
    # =====================================================

    def _get_repository_profile(
        self,
        repository_id: str | None = None,
    ):

        if not repository_id:
            return None

        profile = redis_client.get(
            f"profile:repository:{repository_id}"
        )

        if not profile:
            return None

        try:
            return json.loads(profile)

        except Exception:

            return None

    # =====================================================
    # Execute
    # =====================================================

    def execute(
        self,
        query: str,
        repository_id: str | None = None,
    ):

        print(
            "\n========== REPOSITORY TOOL =========="
        )

        print(
            "Repository Query:",
            query,
        )

        print(
            "Repository ID:",
            repository_id,
        )

        if not repository_id:

            print(
                "No repository_id provided."
            )

            print(
                "=====================================\n"
            )

            return {}

        profile = self._get_repository_profile(
            repository_id
        )

        if not profile:

            print(
                "No repository profile found for:",
                repository_id,
            )

            print(
                "=====================================\n"
            )

            return {}

        result = {
            "repository_id": repository_id,
            "repository_profile": profile,
        }

        print(
            "\nRepository Tool Result:"
        )

        print(
            result
        )

        print(
            "=====================================\n"
        )

        return result

    # =====================================================
    # Existing Metadata Fallback
    # =====================================================

    def _execute_from_metadata(
        self,
        query: str,
    ):

        query = query.lower()

        if any(
            keyword in query
            for keyword in [
                "summary",
                "overview",
                "repository",
                "project",
            ]
        ):

            result = self.metadata.get_summary()

        elif any(
            keyword in query
            for keyword in [
                "architecture",
                "design",
                "pipeline",
                "workflow",
                "indexing",
            ]
        ):

            result = self.metadata.get_architecture()

        elif any(
            keyword in query
            for keyword in [
                "service",
                "services",
            ]
        ):

            result = self.metadata.get_services()

        elif any(
            keyword in query
            for keyword in [
                "route",
                "routes",
                "endpoint",
                "api",
            ]
        ):

            result = self.metadata.get_routes()

        elif any(
            keyword in query
            for keyword in [
                "model",
                "models",
            ]
        ):

            result = self.metadata.get_models()

        elif any(
            keyword in query
            for keyword in [
                "statistics",
                "stats",
                "count",
                "numbers",
            ]
        ):

            result = self.metadata.get_statistics()

        elif any(
            keyword in query
            for keyword in [
                "module",
                "modules",
                "package",
                "packages",
            ]
        ):

            result = self.metadata.get_modules()

        elif any(
            keyword in query
            for keyword in [
                "framework",
                "frameworks",
                "technology",
                "technologies",
                "library",
                "libraries",
            ]
        ):

            result = self.metadata.get_frameworks()

        elif any(
            keyword in query
            for keyword in [
                "dependency",
                "dependencies",
                "requirement",
                "requirements",
            ]
        ):

            result = self.metadata.get_dependencies()

        elif any(
            keyword in query
            for keyword in [
                "language",
                "languages",
            ]
        ):

            result = self.metadata.get_languages()

        else:

            result = self.metadata.get_summary()

        return result

    # =====================================================
    # Select Relevant Metadata
    # =====================================================

    def _select_relevant_metadata(
        self,
        profile: dict,
        query: str,
    ) -> dict:

        query_lower = query.lower()

        selected = {}

        # =================================================
        # Repository Identity
        # =================================================

        always_include = [
            "repository_id",
            "repository_name",
        ]

        for key in always_include:

            if key in profile:

                selected[key] = profile[key]

        # =================================================
        # Architecture / Project Overview
        # =================================================

        architecture_keywords = [
            "architecture",
            "architect",
            "design",
            "structure",
            "workflow",
            "pipeline",
            "how is the project organized",
            "how does the project work",
            "overview",
        ]

        if any(
            keyword in query_lower
            for keyword in architecture_keywords
        ):

            for key in [
                "summary",
                "architecture",
                "modules",
                "services",
                "routes",
                "models",
                "statistics",
            ]:

                if key in profile:

                    selected[key] = profile[key]

        # =================================================
        # Technology Stack
        # =================================================

        technology_keywords = [
            "tech stack",
            "technology",
            "technologies",
            "framework",
            "frameworks",
            "library",
            "libraries",
            "database",
            "databases",
            "language",
            "languages",
            "stack",
        ]

        if any(
            keyword in query_lower
            for keyword in technology_keywords
        ):

            for key in [
                "languages",
                "frameworks",
                "databases",
                "vector_databases",
                "llm_frameworks",
                "llm_providers",
            ]:

                if key in profile:

                    selected[key] = profile[key]

        # =================================================
        # Statistics
        # =================================================

        statistics_keywords = [
            "statistics",
            "stats",
            "count",
            "counts",
            "how many",
            "number of",
            "size",
        ]

        if any(
            keyword in query_lower
            for keyword in statistics_keywords
        ):

            for key in [
                "total_files",
                "total_classes",
                "total_functions",
                "total_imports",
                "statistics",
            ]:

                if key in profile:

                    selected[key] = profile[key]

        # =================================================
        # Dependencies
        # =================================================

        dependency_keywords = [
            "dependency",
            "dependencies",
            "requirements",
            "packages",
            "installed packages",
        ]

        if any(
            keyword in query_lower
            for keyword in dependency_keywords
        ):

            if "dependencies" in profile:

                selected["dependencies"] = (
                    profile["dependencies"]
                )

        # =================================================
        # Source Files
        # =================================================

        source_file_keywords = [
            "source files",
            "source file",
            "files",
            "file",
            "file structure",
            "which files",
            "list files",
            "contain",
            "contains",
            "exist",
            "exists",
            "have a",
            "have any",
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".json",
            ".yaml",
            ".yml",
            ".toml",
            ".md",
            ".sql",
            ".html",
            ".css",
        ]

        has_file_query = any(
            re.search(r"\b" + re.escape(kw) + r"\b", query_lower)
            if not kw.startswith(".")
            else kw in query_lower
            for kw in source_file_keywords
        )

        if has_file_query:

            if "source_files" in profile:

                raw_files = profile["source_files"]
                repo_path = profile.get("repository_path", "").replace("\\", "/")

                formatted_files = []
                for f in raw_files:
                    norm_f = f.replace("\\", "/")
                    if repo_path and norm_f.startswith(repo_path):
                        formatted_files.append(norm_f[len(repo_path):].lstrip("/"))
                    else:
                        formatted_files.append(norm_f)

                selected["source_files"] = formatted_files

                queried_files = [
                    w for w in re.findall(r"[\w\.-]+\.[a-zA-Z0-9]+", query)
                    if not w.startswith(".")
                ]

                if queried_files:

                    existence = {}
                    for qf in queried_files:
                        qf_lower = qf.lower()
                        matches = [
                            f for f in formatted_files
                            if f.lower().endswith("/" + qf_lower) or f.lower() == qf_lower
                        ]
                        existence[qf] = {
                            "exists": len(matches) > 0,
                            "matching_paths": matches,
                        }

                    selected["file_existence_check"] = existence

        # =================================================
        # Default Compact Metadata
        # =================================================

        if not selected:

            for key in [
                "languages",
                "frameworks",
                "databases",
                "vector_databases",
                "llm_frameworks",
                "llm_providers",
                "statistics",
            ]:

                if key in profile:

                    selected[key] = profile[key]

        return selected

    # =====================================================
    # Global Selection Candidates
    # =====================================================

    def get_candidates(
        self,
        query: str,
        repository_id: str | None = None,
    ) -> list[dict]:

        print(
            "\n========== REPOSITORY CANDIDATES =========="
        )

        print(
            "Repository ID:",
            repository_id,
        )

        # -------------------------------------------------
        # Repository ID Required
        # -------------------------------------------------

        if not repository_id:

            print(
                "No repository_id provided."
            )

            print(
                "============================================\n"
            )

            return []

        # -------------------------------------------------
        # Retrieve Actual Repository Profile
        # -------------------------------------------------

        profile = self._get_repository_profile(
            repository_id
        )

        if not profile:

            print(
                "No repository profile found for:",
                repository_id,
            )

            print(
                "============================================\n"
            )

            return []

        # -------------------------------------------------
        # Select Metadata Relevant To This Question
        # -------------------------------------------------

        relevant_metadata = (
            self._select_relevant_metadata(
                profile,
                query,
            )
        )

        # Always preserve repository ID
        relevant_metadata[
            "repository_id"
        ] = repository_id

        # -------------------------------------------------
        # Candidate
        # -------------------------------------------------

        candidate = {
            "source": "repository",
            "type": "metadata",
            "category": "repository_profile",
            "name": "repository_profile",
            "content": json.dumps(
                relevant_metadata,
                indent=2,
                default=str,
            ),
            "rank": 0,
        }

        print(
            "\nRelevant Repository Metadata:"
        )

        print(
            relevant_metadata
        )

        print(
            "\nRepository Candidate:"
        )

        print(
            candidate
        )

        print(
            "============================================\n"
        )

        return [
            candidate
        ]