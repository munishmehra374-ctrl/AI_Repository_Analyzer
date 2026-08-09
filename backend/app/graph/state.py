from typing import Optional, TypedDict


class GraphState(TypedDict):

    # ----------------------------------
    # User Input
    # ----------------------------------

    question: str

    # ----------------------------------
    # Repository Information
    # ----------------------------------

    repository_uploaded: bool
    repository_indexed: bool
    repository_name: Optional[str]
    primary_language: Optional[str]

    # ----------------------------------
    # Planner Output
    # ----------------------------------

    question_type: Optional[str]
    tools: list[str]
    reason: Optional[str]

    # ----------------------------------
    # Tool Outputs
    # ----------------------------------

    retrieval_context: Optional[str]
    graph_context: Optional[str]
    repository_context: Optional[str]

    # ----------------------------------
    # Aggregated Context
    # ----------------------------------

    context: Optional[str]

    # ----------------------------------
    # Analysis
    # ----------------------------------

    analysis: Optional[str]

    # ----------------------------------
    # Root Cause Analysis
    # ----------------------------------

    root_cause: Optional[str]

    # ----------------------------------
    # Review
    # ----------------------------------

    review: Optional[str]

    # ----------------------------------
    # Final Answer
    # ----------------------------------

    answer: Optional[str]