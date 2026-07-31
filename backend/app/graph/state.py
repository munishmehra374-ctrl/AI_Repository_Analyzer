from typing import TypedDict, Optional


class GraphState(TypedDict):
    question: str

    repository_uploaded: bool
    repository_indexed: bool
    repository_name: Optional[str]
    primary_language: Optional[str]

    question_type: Optional[str]
    needs_retrieval: bool

    context: str
    answer: str