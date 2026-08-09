from __future__ import annotations


class RepositoryMetadata:
    """
    Repository Profile

    Stores high-level information about the repository.
    This data is derived from the AST and is used by the
    planner to answer repository-level questions.

    It DOES NOT store:
    - Source code
    - Chunks
    - Graph relationships
    """

    def __init__(self):

        # ==========================================
        # Repository Information
        # ==========================================

        self.repository_name = ""
        self.repository_path = ""

        # ==========================================
        # Statistics
        # ==========================================

        self.total_files = 0
        self.total_classes = 0
        self.total_functions = 0
        self.total_imports = 0

        # (Future)
        self.total_routes = 0
        self.total_models = 0

        # ==========================================
        # Technologies
        # ==========================================

        self.languages = set()

        self.frameworks = set()

        self.dependencies = set()

        self.databases = set()

        self.vector_databases = set()

        self.llm_frameworks = set()

        self.llm_providers = set()

        # ==========================================
        # Repository Structure
        # ==========================================

        self.modules = set()

        self.entry_points = set()

        # ==========================================
        # Architecture
        # ==========================================

        self.architecture = ""

        self.design_patterns = set()

        # ==========================================
        # Repository Summary
        # ==========================================

        self.summary = ""