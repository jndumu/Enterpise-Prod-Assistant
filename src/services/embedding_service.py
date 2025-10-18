"""Production embedding service with configurable providers."""

import logging
from typing import List, Union
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class EmbeddingProvider(ABC):
    """Abstract embedding provider interface."""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text."""
        pass
    
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding dimension."""
        pass

class HuggingFaceProvider(EmbeddingProvider):
    """HuggingFace/SentenceTransformers provider."""
    
    def __init__(self, model_name: str):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self._dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Loaded HuggingFace model: {model_name}")
        except ImportError:
            raise ImportError("Install: pip install sentence-transformers")
    
    def embed_text(self, text: str) -> List[float]:
        return self.model.encode(text, convert_to_tensor=False).tolist()
    
    @property
    def dimension(self) -> int:
        return self._dimension

class GoogleProvider(EmbeddingProvider):
    """Google Generative AI provider."""
    
    def __init__(self, model_name: str, api_key: str):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model_name = model_name
            self._dimension = 768  # Google embedding dimension
            logger.info(f"Configured Google model: {model_name}")
        except ImportError:
            raise ImportError("Install: pip install google-generativeai")
    
    def embed_text(self, text: str) -> List[float]:
        import google.generativeai as genai
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_document"
        )
        return result["embedding"]
    
    @property
    def dimension(self) -> int:
        return self._dimension

class OpenAIProvider(EmbeddingProvider):
    """OpenAI embeddings provider."""
    
    def __init__(self, model_name: str, api_key: str):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
            self.model_name = model_name
            self._dimension = 1536 if "3-small" in model_name else 1536
            logger.info(f"Configured OpenAI model: {model_name}")
        except ImportError:
            raise ImportError("Install: pip install openai")
    
    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding
    
    @property
    def dimension(self) -> int:
        return self._dimension

class CohereProvider(EmbeddingProvider):
    """Cohere embeddings provider."""
    
    def __init__(self, model_name: str, api_key: str):
        try:
            import cohere
            self.client = cohere.Client(api_key)
            self.model_name = model_name
            self._dimension = 1024  # Cohere embedding dimension
            logger.info(f"Configured Cohere model: {model_name}")
        except ImportError:
            raise ImportError("Install: pip install cohere")
    
    def embed_text(self, text: str) -> List[float]:
        response = self.client.embed(texts=[text], model=self.model_name)
        return response.embeddings[0]
    
    @property
    def dimension(self) -> int:
        return self._dimension

class EmbeddingService:
    """Main embedding service with provider abstraction."""
    
    def __init__(self, provider_name: str, model_name: str, api_key: str = None):
        self.provider = self._create_provider(provider_name, model_name, api_key)
        logger.info(f"EmbeddingService initialized with {provider_name}")
    
    def _create_provider(self, provider_name: str, model_name: str, api_key: str) -> EmbeddingProvider:
        """Factory method to create embedding provider."""
        provider_name = provider_name.lower()
        
        if provider_name == "huggingface":
            return HuggingFaceProvider(model_name)
        elif provider_name == "google":
            if not api_key:
                raise ValueError("Google provider requires API key")
            return GoogleProvider(model_name, api_key)
        elif provider_name == "openai":
            if not api_key:
                raise ValueError("OpenAI provider requires API key")
            return OpenAIProvider(model_name, api_key)
        elif provider_name == "cohere":
            if not api_key:
                raise ValueError("Cohere provider requires API key")
            return CohereProvider(model_name, api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    def embed(self, text: str) -> List[float]:
        """Generate embedding for text."""
        try:
            return self.provider.embed_text(text)
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            raise
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        return [self.embed(text) for text in texts]
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self.provider.dimension