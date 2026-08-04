from app.services.retrieval_service import RetrievalService


class RetrievalTool:

    def __init__(
        self,
        retrieval_service: RetrievalService,
    ):

        self.retrieval_service = retrieval_service

    def execute(
        self,
        question: str,
    ) -> str:

        print("\n========== RETRIEVAL TOOL ==========")
        print("Question:", question)

        result = self.retrieval_service.retrieve(
            question
        )

        print("\nRetrieved Context:")
        print(result)
        print("====================================\n")

        return result