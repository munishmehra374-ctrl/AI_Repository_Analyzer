from app.vectorstore.chroma_store import ChromaStore


class RepositoryRetriever:

    # Maximum number of chunks allowed from one file
    MAX_CHUNKS_PER_FILE = 3

    def __init__(self, vector_store: ChromaStore):
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        repository_id: str | None = None,
    ):
        if not query.strip():
            return []

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if not repository_id:
            raise ValueError(
                "repository_id is required for repository retrieval."
            )

        # Retrieve extra candidates first.
        raw_k = max(
            top_k * 3,
            top_k,
        )

        # ----------------------------------------------------------
        # Repository-specific Chroma search
        # ----------------------------------------------------------

        retriever = (
            self.vector_store.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": raw_k,
                    "filter": {
                        "repository_id": repository_id
                    },
                },
            )
        )

        # ==========================================================
        # VECTOR SEARCH DEBUG
        # ==========================================================

        print(
            "\n========== VECTOR SEARCH DEBUG =========="
        )

        print(
            "Query:"
        )

        print(
            query
        )

        print(
            "Repository ID:"
        )

        print(
            repository_id
        )

        print(
            "Raw K:"
        )

        print(
            raw_k
        )

        print(
            "Chroma collection count:"
        )

        try:

            collection_data = (
                self.vector_store.vectorstore.get(
                    where={
                        "repository_id": repository_id
                    }
                )
            )

            ids = collection_data.get(
                "ids",
                []
            )

            metadatas = collection_data.get(
                "metadatas",
                []
            )

            print(
                "IDs:",
                len(ids)
            )

            print(
                "Metadatas:",
                len(metadatas)
            )

            if ids:

                print(
                    "\nFirst 5 Chroma IDs:"
                )

                for i, document_id in enumerate(
                    ids[:5]
                ):

                    print(
                        i,
                        document_id
                    )

            if metadatas:

                print(
                    "\nFirst 5 metadata entries:"
                )

                for i, metadata in enumerate(
                    metadatas[:5]
                ):

                    print(
                        i,
                        metadata
                    )

        except Exception as e:

            print(
                "CHROMA GET FAILED:"
            )

            print(
                "Exception type:",
                type(e).__name__
            )

            print(
                "Exception:",
                str(e)
            )

        print(
            "=========================================\n"
        )

        # ----------------------------------------------------------
        # Actual vector search
        # ----------------------------------------------------------

        print(
            "========== CALLING CHROMA SIMILARITY SEARCH =========="
        )

        try:

            docs = retriever.invoke(
                query
            )

            print(
                "VECTOR SEARCH SUCCESS."
            )

            print(
                "Documents returned:",
                len(docs)
            )

        except Exception as e:

            print(
                "VECTOR SEARCH FAILED:"
            )

            print(
                "Exception type:",
                type(e).__name__
            )

            print(
                "Exception:",
                str(e)
            )

            raise

        print(
            "\n========== VECTOR SEARCH =========="
        )

        print(
            "Repository:",
            repository_id,
        )

        print(
            "Raw documents:",
            len(docs),
        )

        # ==========================================================
        # Diversity Filtering
        # ==========================================================

        diversified_docs = []

        file_counts = {}

        for doc in docs:

            # Extra safety check so another repository
            # can never enter the result set.
            if (
                doc.metadata.get(
                    "repository_id"
                )
                != repository_id
            ):
                continue

            file_path = str(
                doc.metadata.get(
                    "file_path",
                    "",
                )
            )

            if not file_path:
                file_path = (
                    f"__unknown_file_{len(diversified_docs)}"
                )

            current_count = file_counts.get(
                file_path,
                0,
            )

            if (
                current_count
                >= self.MAX_CHUNKS_PER_FILE
            ):
                continue

            diversified_docs.append(doc)

            file_counts[file_path] = (
                current_count + 1
            )

            if len(diversified_docs) >= top_k:
                break

        # ==========================================================
        # Debug
        # ==========================================================

        print(
            "Diversified documents:",
            len(diversified_docs),
        )

        print(
            "\n----- Selected Files -----"
        )

        for index, doc in enumerate(
            diversified_docs
        ):

            print(
                f"{index}:",
                doc.metadata.get(
                    "name"
                ),
                "|",
                doc.metadata.get(
                    "qualified_name"
                ),
                "|",
                doc.metadata.get(
                    "file_path"
                ),
            )

        print(
            "===================================\n"
        )

        return diversified_docs