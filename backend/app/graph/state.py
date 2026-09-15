from typing import Optional, TypedDict


class GraphState(TypedDict):

    # ----------------------------------
    # User Input
    # ----------------------------------

    question: str

    # ----------------------------------
    # Chat Title
    # ----------------------------------

    generate_title: bool
    title: Optional[str]
    
    # ----------------------------------
    # Repository Information
    # ----------------------------------

    repository_uploaded: bool
    repository_indexed: bool
    repository_id: Optional[str]
    repository_name: Optional[str]
    primary_language: Optional[str]

    # ----------------------------------
    # Planner Output
    # ----------------------------------

    question_type: Optional[str]
    tools: list[str]
    reason: Optional[str]
    deep_analysis: bool

    # ----------------------------------
    # Tool Outputs
    # ----------------------------------

    retrieval_context: Optional[str]
    graph_context: Optional[str]
    repository_context: Optional[str]

    # ----------------------------------
    # NEW: Global Selection Candidates
    # ----------------------------------

    retrieval_candidates: list[dict]
    graph_candidates: list[dict]
    repository_candidates: list[dict]

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