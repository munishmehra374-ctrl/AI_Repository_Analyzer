from app.services.retrieval_service import RetrievalService


class RetrievalTool:

    def __init__(
        self,
        retrieval_service: RetrievalService,
    ):
        self.retrieval_service = retrieval_service

    def execute(
        self,
        query: str,
    ) -> str:

        print("\n========== RETRIEVAL TOOL ==========")
        print("Retrieval Query:", query)

        result = self.retrieval_service.retrieve(
            query
        )

        print("\nRetrieved Context:")
        print(result)
        print("====================================\n")

        return result