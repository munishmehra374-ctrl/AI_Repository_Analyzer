from pathlib import Path
from git import Repo


class CloneService:
    def __init__(self):
        self.clone_directory = Path("cloned_repos")
        self.clone_directory.mkdir(exist_ok=True)

    def clone_repository(self, repo_url: str):
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]

        destination = (self.clone_directory / repo_name).resolve()

        if destination.exists():
            return {
                "status": "already_exists",
                "repository": repo_name,
                "path": str(destination)
            }

        try:
            Repo.clone_from(repo_url, destination)
        except Exception as e:
            raise RuntimeError(f"Failed to clone repository from '{repo_url}': {e}") from e

        return {
            "status": "success",
            "repository": repo_name,
            "path": str(destination)
        }