from __future__ import annotations

import os

from app.metadata.repository_metadata import RepositoryMetadata
from app.metadata.statistics_analyzer import StatisticsAnalyzer
from app.metadata.module_analyzer import ModuleAnalyzer
from app.metadata.technology_detector import TechnologyDetector
from app.metadata.system_architecture import (
    SYSTEM_SUMMARY,
    INDEXING_PIPELINE,
    QUESTION_ANSWERING_PIPELINE,
)


class RepositoryMetadataService:
    """
    Repository Profiler

    Coordinates all repository analyzers and builds
    the RepositoryMetadata object.
    """

    def __init__(self):

        self.repository = RepositoryMetadata()

        self.statistics_analyzer = StatisticsAnalyzer()

        self.module_analyzer = ModuleAnalyzer()

        self.technology_detector = TechnologyDetector()

    # =====================================================
    # Update Metadata For One File
    # =====================================================

    def update(
        self,
        extracted_data: dict,
        file_path: str,
        repository_path: str,
        language: str = "python",
    ):

        # -------------------------------------------------
        # Repository Information
        # -------------------------------------------------

        if not self.repository.repository_name:

            self.repository.repository_name = os.path.basename(
                repository_path
            )

            self.repository.repository_path = repository_path

        # -------------------------------------------------
        # Statistics Analyzer
        # -------------------------------------------------

        statistics = self.statistics_analyzer.analyze(
            extracted_data
        )

        self.repository.total_files += 1

        self.repository.total_classes += statistics[
            "total_classes"
        ]

        self.repository.total_functions += statistics[
            "total_functions"
        ]

        self.repository.total_imports += statistics[
            "total_imports"
        ]

        # -------------------------------------------------
        # Language
        # -------------------------------------------------

        self.repository.languages.add(language)

        # -------------------------------------------------
        # Module Analyzer
        # -------------------------------------------------

        module = self.module_analyzer.analyze(
            file_path
        )

        if module["module"]:

            self.repository.modules.add(
                module["module"]
            )

        # -------------------------------------------------
        # Technology Detector
        # -------------------------------------------------

        technologies = self.technology_detector.detect(
            extracted_data.get(
                "imports",
                [],
            )
        )

        self.repository.frameworks.update(
            technologies["frameworks"]
        )

        self.repository.databases.update(
            technologies["databases"]
        )

        self.repository.vector_databases.update(
            technologies["vector_databases"]
        )

        self.repository.llm_frameworks.update(
            technologies["llm_frameworks"]
        )

        self.repository.llm_providers.update(
            technologies["llm_providers"]
        )

        self.repository.dependencies.update(
            technologies["dependencies"]
        )

        # -------------------------------------------------
        # Repository Summary
        # -------------------------------------------------

        self.repository.summary = (
            "AI Repository Analyzer that indexes source code using "
            "AST extraction, semantic chunking, hybrid retrieval "
            "(ChromaDB + BM25), Neo4j Knowledge Graph, and "
            "Repository Metadata."
        )

        # -------------------------------------------------
        # Repository Architecture
        # -------------------------------------------------

        self.repository.architecture = (
            "Repository Reader -> AST Extraction -> Semantic Chunking -> "
            "ChromaDB + BM25 + Neo4j Knowledge Graph + Repository Metadata"
        )

    # =====================================================
    # Build Metadata From ALL Extracted Files
    # =====================================================

    def build_from_extracted_data(
        self,
        extracted_files: list[dict],
        repository_path: str,
        language: str = "python",
    ):
        """
        Rebuild repository metadata from the complete set
        of extracted files.

        This is important for incremental indexing:

        - changed files are freshly extracted
        - unchanged files are loaded from Redis
        - metadata must be calculated from BOTH

        This prevents the dashboard from showing only the
        number of files changed during the latest indexing run.
        """

        # Start with a completely fresh metadata object.
        self.repository = RepositoryMetadata()

        for extracted_data in extracted_files:

            file_path = extracted_data.get(
                "file_path"
            )

            if not file_path:
                continue

            self.update(
                extracted_data=extracted_data,
                file_path=file_path,
                repository_path=repository_path,
                language=extracted_data.get(
                    "language",
                    language,
                ),
            )

        return self.get_repository_profile()

    # =====================================================
    # Repository Profile
    # =====================================================

    def get_repository_profile(self):

        return {
            "repository_name":
                self.repository.repository_name,

            "repository_path":
                self.repository.repository_path,

            "summary":
                self.repository.summary,

            "architecture":
                self.repository.architecture,

            "statistics": {
                "files":
                    self.repository.total_files,

                "classes":
                    self.repository.total_classes,

                "functions":
                    self.repository.total_functions,

                "imports":
                    self.repository.total_imports,
            },

            "languages":
                sorted(self.repository.languages),

            "frameworks":
                sorted(self.repository.frameworks),

            "databases":
                sorted(self.repository.databases),

            "vector_databases":
                sorted(self.repository.vector_databases),

            "llm_frameworks":
                sorted(self.repository.llm_frameworks),

            "llm_providers":
                sorted(self.repository.llm_providers),

            "dependencies":
                sorted(self.repository.dependencies),

            "modules":
                sorted(self.repository.modules),

            "design_patterns":
                sorted(self.repository.design_patterns),
        }

    # =====================================================
    # Repository Summary
    # =====================================================

    def get_summary(self):

        profile = self.get_repository_profile()

        return f"""
Repository Name
---------------
{profile["repository_name"]}

Summary
-------
{SYSTEM_SUMMARY.strip()}

Repository Statistics
---------------------
Files: {profile["statistics"]["files"]}
Classes: {profile["statistics"]["classes"]}
Functions: {profile["statistics"]["functions"]}
Imports: {profile["statistics"]["imports"]}

Languages
---------
{", ".join(profile["languages"]) or "None"}

Frameworks
----------
{", ".join(profile["frameworks"]) or "None"}

Databases
---------
{", ".join(profile["databases"]) or "None"}

Vector Databases
----------------
{", ".join(profile["vector_databases"]) or "None"}

LLM Frameworks
--------------
{", ".join(profile["llm_frameworks"]) or "None"}

LLM Providers
-------------
{", ".join(profile["llm_providers"]) or "None"}

Modules
-------
{", ".join(profile["modules"]) or "None"}
"""

    # =====================================================
    # Architecture
    # =====================================================

    def get_architecture(self):

        profile = self.get_repository_profile()

        indexing_pipeline = "\n".join(
            f"  {i + 1}. {step}"
            for i, step in enumerate(INDEXING_PIPELINE)
        )

        qa_pipeline = "\n".join(
            f"  {i + 1}. {step}"
            for i, step in enumerate(QUESTION_ANSWERING_PIPELINE)
        )

        return f"""
Repository Architecture
=======================

Repository Information
----------------------

Repository:
{profile["repository_name"]}

Primary Language:
{", ".join(profile["languages"]) or "Unknown"}

Frameworks:
{", ".join(profile["frameworks"]) or "None"}

Databases:
{", ".join(profile["databases"]) or "None"}

Vector Databases:
{", ".join(profile["vector_databases"]) or "None"}

Modules:
{", ".join(profile["modules"]) or "None"}

----------------------------------------------------
Indexing Pipeline
----------------------------------------------------

{indexing_pipeline}

----------------------------------------------------
Question Answering Pipeline
----------------------------------------------------

{qa_pipeline}

----------------------------------------------------
Knowledge Sources
----------------------------------------------------

• AST Extraction
• Semantic Chunks
• ChromaDB Vector Store
• BM25 Index
• Neo4j Knowledge Graph
• Repository Metadata

----------------------------------------------------
System Summary
----------------------------------------------------

{SYSTEM_SUMMARY.strip()}
"""

    # =====================================================
    # Statistics
    # =====================================================

    def get_statistics(self):

        return self.get_repository_profile()["statistics"]

    # =====================================================
    # Modules
    # =====================================================

    def get_modules(self):

        return self.get_repository_profile()["modules"]

    # =====================================================
    # Services
    # =====================================================

    def get_services(self):

        modules = self.get_repository_profile()["modules"]

        return [
            module
            for module in modules
            if "service" in module.lower()
        ]

    # =====================================================
    # Routes
    # =====================================================

    def get_routes(self):

        return []

    # =====================================================
    # Models
    # =====================================================

    def get_models(self):

        modules = self.get_repository_profile()["modules"]

        return [
            module
            for module in modules
            if "model" in module.lower()
        ]

    # =====================================================
    # Frameworks
    # =====================================================

    def get_frameworks(self):

        return self.get_repository_profile()["frameworks"]

    # =====================================================
    # Dependencies
    # =====================================================

    def get_dependencies(self):

        return self.get_repository_profile()["dependencies"]

    # =====================================================
    # Languages
    # =====================================================

    def get_languages(self):

        return self.get_repository_profile()["languages"]