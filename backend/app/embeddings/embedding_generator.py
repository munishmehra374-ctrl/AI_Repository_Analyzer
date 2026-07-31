from sentence_transformers import SentenceTransformer


class EmbeddingGenerator:

    def __init__(self):

        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def generate(self, chunks):

        embedded_chunks = []

        for chunk in chunks:

            embedding = self.model.encode(
                chunk["code"],
                normalize_embeddings=True
            ).tolist()

            embedded_chunks.append({

                **chunk,

                "embedding": embedding

            })

        return embedded_chunks