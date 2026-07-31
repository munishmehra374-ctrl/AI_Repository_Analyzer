from langchain_huggingface import HuggingFaceEmbeddings


class EmbeddingModel:

    def __init__(self):

        self.model = HuggingFaceEmbeddings(

            model_name="BAAI/bge-small-en-v1.5",

            model_kwargs={
                "device": "cpu"
            },

            encode_kwargs={
                "normalize_embeddings": True
            }

        )

    def embed_documents(self, texts: list[str]):

        return self.model.embed_documents(texts)

    def embed_query(self, text: str):

        return self.model.embed_query(text)