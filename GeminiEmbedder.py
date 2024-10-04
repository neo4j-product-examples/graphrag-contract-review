from neo4j_graphrag.embedder import Embedder
from typing import Any
from vertexai.language_models import TextEmbeddingModel

class GeminiEmbedder(Embedder):
    def __init__(self, model_name: str = "textembedding-gecko@003") -> None:
        try:
             import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "Could not import google genai client. "
                "Please install it with `pip install google-generativeai`."
            )
        #make sure env variable GOOGLE_API_KEY is set 
        genai.configure()
        self.model = TextEmbeddingModel.from_pretrained(model_name=model_name)
        
    
    def embed_query(self, text: str, output_dimensionality=None,**kwargs: Any) -> list[float]:
        text_embeddings = self.model.get_embeddings([text],output_dimensionality=output_dimensionality)
        return text_embeddings[0].values
