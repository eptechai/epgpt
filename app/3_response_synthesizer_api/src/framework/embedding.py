
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


from variables import EMBEDDING_MODEL


class EmbeddingModel:

    def __init__(self, embedding_type: str):
        self.embedding_type = embedding_type
        self.set_embedding_model()

    def set_embedding_model(self):
        match self.embedding_type:
            case "huggingface":
                self.embed_model = HuggingFaceEmbedding(
                    model_name=EMBEDDING_MODEL,
                    device="cpu",
                )
                self.embed_dim = self.embed_model._model._modules["1"].word_embedding_dimension