from __future__ import annotations

import os

from app.metadata.repository_metadata import RepositoryMetadata

from app.metadata.statistics_analyzer import StatisticsAnalyzer
from app.metadata.module_analyzer import ModuleAnalyzer
from app.metadata.technology_detector import TechnologyDetector


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
    # Update Repository Profile
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

    # =====================================================
    # Repository Profile
    # =====================================================

    def get_repository_profile(self):

        return {

            "repository_name":
                self.repository.repository_name,

            "repository_path":
                self.repository.repository_path,

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

                sorted(
                    self.repository.languages
                ),

            "frameworks":

                sorted(
                    self.repository.frameworks
                ),

            "databases":

                sorted(
                    self.repository.databases
                ),

            "vector_databases":

                sorted(
                    self.repository.vector_databases
                ),

            "llm_frameworks":

                sorted(
                    self.repository.llm_frameworks
                ),

            "llm_providers":

                sorted(
                    self.repository.llm_providers
                ),

            "dependencies":

                sorted(
                    self.repository.dependencies
                ),

            "modules":

                sorted(
                    self.repository.modules
                ),

            "architecture":

                self.repository.architecture,

            "design_patterns":

                sorted(
                    self.repository.design_patterns
                ),

            "summary":

                self.repository.summary,
        }