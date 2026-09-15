import inspect

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
        repository_id: str | None = None,
    ) -> str:

        print(
            "\n========== RETRIEVAL TOOL =========="
        )

        print(
            "Retrieval Query:",
            query,
        )

        print(
            "Repository ID:",
            repository_id,
        )

        # =====================================================
        # Runtime diagnostic
        # =====================================================

        print(
            "\n========== RUNTIME RETRIEVAL DEBUG =========="
        )

        print(
            "RetrievalService class:",
            self.retrieval_service.__class__,
        )

        print(
            "RetrievalService file:",
            inspect.getfile(
                self.retrieval_service.__class__
            ),
        )

        print(
            "retrieve() file:",
            inspect.getsourcefile(
                self.retrieval_service.retrieve
            ),
        )

        print(
            "==============================================\n"
        )

        # =====================================================
        # Retrieval
        # =====================================================

        result = self.retrieval_service.retrieve(
            query,
            repository_id=repository_id,
        )

        print(
            "\nRetrieved Context:"
        )

        print(result)

        print(
            "====================================\n"
        )

        return result

    # =====================================================
    # NEW: GLOBAL SELECTION CANDIDATES
    # =====================================================

    def get_candidates(
        self,
        query: str,
        repository_id: str | None = None,
    ) -> list[dict]:

        print(
            "\n========== RETRIEVAL CANDIDATES =========="
        )

        results = self.retrieval_service.retrieve(
            query,
            return_candidates=True,
            repository_id=repository_id,
        )

        print(
            "Retrieval candidates:",
            len(results),
        )

        print(
            "============================================\n"
        )

        return results