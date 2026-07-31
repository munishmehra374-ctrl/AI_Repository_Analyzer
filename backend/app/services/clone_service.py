from pathlib import Path
from git import Repo


class CloneService:
    def __init__(self):
        self.clone_directory = Path("cloned_repos")
        self.clone_directory.mkdir(exist_ok=True)

    def clone_repository(self, repo_url: str):
        repo_name = repo_url.rstrip("/").split("/")[-1]

        destination = self.clone_directory / repo_name

        if destination.exists():
            return {
                "status": "already_exists",
                "repository": repo_name,
                "path": str(destination)
            }

        Repo.clone_from(repo_url, destination)

        return {
            "status": "success",
            "repository": repo_name,
            "path": str(destination)
        }