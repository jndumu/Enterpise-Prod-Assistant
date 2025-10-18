"""Model loader: dynamically load LLMs and embedding backends from .env and config.
Keeps under 200 LOC, production-oriented, async-safe, pluggable providers.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from src.core.utils.config_loader import get_config, load_env
from src.core.logging.custom_logger import CustomLogger
from src.core.exceptions.custom_exception import ResearchAnalystException


# Global logger (shared style with rest of project)
GLOBAL_LOGGER = CustomLogger().get_logger(__name__)


class ApiKeyManager:
    """Loads and validates API keys from environment; logs presence/absence."""

    REQUIRED_KEYS = [
        # Generic providers
        "OPENAI_API_KEY",
        "GOOGLE_API_KEY",
        "GROQ_API_KEY",
        "HUGGINGFACE_API_KEY",
        "AZURE_OPENAI_API_KEY",
        # Astra DB
        "ASTRA_DB_API_ENDPOINT",
        "ASTRA_DB_APPLICATION_TOKEN",
        "ASTRA_DB_KEYSPACE",
    ]

    def __init__(self) -> None:
        load_env()  # project helper around load_dotenv
        load_dotenv(override=False)
        self.env = {k: os.getenv(k) for k in self.REQUIRED_KEYS}
        self.env["LLM_PROVIDER"] = os.getenv("LLM_PROVIDER", "openai").lower()
        self._log_summary()

    def _log_summary(self) -> None:
        for k, v in self.env.items():
            if k in ("ASTRA_DB_APPLICATION_TOKEN", "OPENAI_API_KEY", "GOOGLE_API_KEY", "GROQ_API_KEY", "AZURE_OPENAI_API_KEY", "HUGGINGFACE_API_KEY"):
                GLOBAL_LOGGER.info("env_key", key=k, present=bool(v))
            else:
                GLOBAL_LOGGER.info("env_value", key=k, value=v)

    def get(self, key: str) -> Optional[str]:
        return self.env.get(key)

    def require(self, key: str) -> str:
        val = self.get(key)
        if not val:
            raise ResearchAnalystException(f"Missing required env key: {key}")
        return val


class ModelLoader:
    """Loads embedding models and LLMs based on config.yaml and .env.
    Providers supported (embeddings): google, huggingface
    Providers supported (LLM): openai, google (gemini), groq, huggingface, azure-openai
    """

    def __init__(self, cfg: Optional[Dict[str, Any]] = None, keys: Optional[ApiKeyManager] = None) -> None:
        self.cfg = cfg or get_config()
        self.keys = keys or ApiKeyManager()
        self.logger = GLOBAL_LOGGER

    # ---------- Embeddings ----------
    def load_embeddings(self):
        emb_cfg = (self.cfg.get("embedding_model") or {})
        provider = (emb_cfg.get("provider") or os.getenv("EMBEDDING_PROVIDER") or "google").lower()
        model_name = emb_cfg.get("model_name") or os.getenv("EMBEDDING_MODEL") or "models/text-embedding-004"

        self.logger.info("embedding_config", provider=provider, model=model_name)

        if provider == "google":
            try:
                import google.generativeai as genai
            except Exception as e:
                raise ResearchAnalystException(f"google.generativeai not installed: {e}")
            api_key = self.keys.require("GOOGLE_API_KEY")
            genai.configure(api_key=api_key)

            def embed_fn(text: str):
                res = genai.embed_content(model=model_name, content=text, task_type="retrieval_document")
                return res["embedding"]

            return {"provider": provider, "model": model_name, "embed": embed_fn}

        if provider == "huggingface":
            try:
                from sentence_transformers import SentenceTransformer
            except Exception as e:
                raise ResearchAnalystException(f"sentence-transformers not installed: {e}")
            # Optional: private model auth via HUGGINGFACE_API_KEY
            if os.getenv("HUGGINGFACE_API_KEY"):
                os.environ["HF_TOKEN"] = os.getenv("HUGGINGFACE_API_KEY", "")
            model = SentenceTransformer(model_name)

            def embed_fn(text: str):
                return model.encode(text).tolist()

            return {"provider": provider, "model": model_name, "embed": embed_fn}

        raise ResearchAnalystException(f"Unsupported embedding provider: {provider}")

    # ---------- LLMs ----------
    def load_llm(self, provider_name: Optional[str] = None):
        llm_cfgs = (self.cfg.get("llm") or {})
        provider = (provider_name or self.keys.get("LLM_PROVIDER") or "openai").lower()
        cfg = llm_cfgs.get(provider) or {}
        model_name = cfg.get("model_name") or os.getenv("LLM_MODEL") or "gpt-4o"
        temperature = cfg.get("temperature", 0)
        max_tokens = cfg.get("max_output_tokens", 2048)

        self.logger.info("llm_config", provider=provider, model=model_name, temperature=temperature, max_tokens=max_tokens)

        if provider == "openai":
            try:
                from openai import OpenAI
            except Exception as e:
                raise ResearchAnalystException(f"openai not installed: {e}")
            client = OpenAI(api_key=self.keys.require("OPENAI_API_KEY"))

            def chat(messages: list[dict[str, str]]):
                res = client.chat.completions.create(model=model_name, messages=messages, temperature=temperature, max_tokens=max_tokens)
                return res.choices[0].message.content

            return {"provider": provider, "model": model_name, "chat": chat}

        if provider == "google":
            try:
                import google.generativeai as genai
            except Exception as e:
                raise ResearchAnalystException(f"google.generativeai not installed: {e}")
            genai.configure(api_key=self.keys.require("GOOGLE_API_KEY"))
            model = genai.GenerativeModel(model_name)

            def chat(messages: list[dict[str, str]]):
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                return model.generate_content(prompt).text

            return {"provider": provider, "model": model_name, "chat": chat}

        if provider == "groq":
            try:
                import groq
            except Exception as e:
                raise ResearchAnalystException(f"groq not installed: {e}")
            client = groq.Client(api_key=self.keys.require("GROQ_API_KEY"))

            def chat(messages: list[dict[str, str]]):
                res = client.chat.completions.create(model=model_name, messages=messages, temperature=temperature, max_tokens=max_tokens)
                return res.choices[0].message.content

            return {"provider": provider, "model": model_name, "chat": chat}

        if provider == "huggingface":
            try:
                from huggingface_hub import InferenceClient
            except Exception as e:
                raise ResearchAnalystException(f"huggingface_hub not installed: {e}")
            token = self.keys.get("HUGGINGFACE_API_KEY")
            client = InferenceClient(model=model_name, token=token)

            def chat(messages: list[dict[str, str]]):
                prompt = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
                return client.text_generation(prompt, max_new_tokens=max_tokens)

            return {"provider": provider, "model": model_name, "chat": chat}

        if provider in ("azure", "azure-openai"):
            try:
                from openai import AzureOpenAI
            except Exception as e:
                raise ResearchAnalystException(f"openai (azure) not installed: {e}")
            client = AzureOpenAI(api_key=self.keys.require("AZURE_OPENAI_API_KEY"))

            def chat(messages: list[dict[str, str]]):
                res = client.chat.completions.create(model=model_name, messages=messages, temperature=temperature, max_tokens=max_tokens)
                return res.choices[0].message.content

            return {"provider": provider, "model": model_name, "chat": chat}

        raise ResearchAnalystException(f"Unsupported LLM provider: {provider}")


__all__ = ["ApiKeyManager", "ModelLoader", "GLOBAL_LOGGER"]

import os
from typing import Callable, List

import google.generativeai as genai


def _init_google(model_name: str) -> Callable[[List[str]], List[List[float]]]:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")
    genai.configure(api_key=api_key)

    def _embed_batch(texts: List[str]) -> List[List[float]]:
        out: List[List[float]] = []
        for t in texts:
            res = genai.embed_content(model=model_name, content=t)
            out.append(res["embedding"])  # type: ignore[index]
        return out

    return _embed_batch


def get_embedding_fn(config: dict) -> Callable[[List[str]], List[List[float]]]:
    provider = ((config or {}).get("embedding_model") or {}).get("provider")
    model_name = ((config or {}).get("embedding_model") or {}).get("model_name")
    if not provider or not model_name:
        raise RuntimeError("embedding_model.provider and embedding_model.model_name are required in config")
    if provider.lower() == "google":
        return _init_google(model_name)
    raise RuntimeError(f"Unsupported embedding provider: {provider}")

