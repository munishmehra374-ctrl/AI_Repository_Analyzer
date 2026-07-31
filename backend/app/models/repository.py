from pydantic import BaseModel


class RepositoryRequest(BaseModel):
    url: str