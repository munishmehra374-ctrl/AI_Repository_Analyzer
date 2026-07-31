from pathlib import Path


class RepositoryReader:
    IGNORE_DIRECTORIES = {
        ".git",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".venv",
        "venv"
    }

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".go",
        ".rs"
    }

    def get_source_files(self, repository_path: str):
        repository = Path(repository_path)

        source_files = []

        for file in repository.rglob("*"):

            if not file.is_file():
                continue

            if any(folder in self.IGNORE_DIRECTORIES for folder in file.parts):
                continue

            if file.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            source_files.append(str(file))

        return source_files