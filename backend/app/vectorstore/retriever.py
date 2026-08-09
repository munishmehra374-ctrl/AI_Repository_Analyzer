from app.vectorstore.chroma_store import ChromaStore


class RepositoryRetriever:

    def __init__(self, vector_store: ChromaStore):
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ):

        retriever = self.vector_store.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": top_k
            }
        )

        docs = retriever.invoke(query)

        print("\n========== VECTOR SEARCH ==========")

        if not docs:

            print("No documents found.")

        else:

            print(
                "Number of documents:",
                len(docs)
            )

            print(
                "\n----- First Document Metadata -----"
            )

            print(
                docs[0].metadata
            )

            print(
                "\n----- First 300 Characters -----"
            )

            print(
                repr(
                    docs[0].page_content[:300]
                )
            )

        print(
            "===================================\n"
        )

        return docs