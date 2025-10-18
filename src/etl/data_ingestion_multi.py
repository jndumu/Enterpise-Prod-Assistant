"""Multi-file ingestion pipeline: parse (Unstructured), chunk, embed, upsert to AstraDB.
Idempotent by deterministic _id to avoid re-inserting previously processed chunks.
"""

from __future__ import annotations

import os
import hashlib
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional

from dotenv import load_dotenv
from unstructured.partition.auto import partition
from astrapy import DataAPIClient

# Ensure project root on sys.path for package imports when executed as a script
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.logging.custom_logger import CustomLogger
from src.core.exceptions.custom_exception import ResearchAnalystException
from src.core.utils.config_loader import get_config
from src.core.utils.model_loader import ModelLoader


logger = CustomLogger().get_logger(__name__)
load_dotenv()


def sha1_hex(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def extract_text_any(path: Path) -> str:
    try:
        elements = partition(filename=str(path))
        parts = [getattr(e, "text", None) or str(e) for e in elements]
        text = "\n".join([p for p in parts if p])
        if not text.strip():
            raise ResearchAnalystException(f"No extractable text in: {path}")
        return text
    except Exception as e:
        raise ResearchAnalystException(f"Extract failed for {path}: {e}")


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    if not text.strip():
        return []
    chunks: List[str] = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        # Prefer sentence boundary near the end
        if end < n:
            k = text.rfind('.', start, end)
            if k > start + chunk_size // 2:
                end = k + 1
        piece = text[start:end].strip()
        if piece:
            chunks.append(piece)
        start = end - overlap
        if start >= n:
            break
    return chunks


class AstraClient:
    def __init__(self, collection_name: str):
        token = os.getenv("ASTRA_DB_TOKEN") or os.getenv("ASTRA_DB_APPLICATION_TOKEN")
        endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
        if not token or not endpoint:
            raise ResearchAnalystException("AstraDB creds missing (token/endpoint)")
        db = DataAPIClient(token=token).get_database_by_api_endpoint(endpoint)
        self.collection = db.get_collection(collection_name)
        logger.info("AstraDB ready", collection=collection_name)

    def upsert_chunk(self, doc: Dict[str, Any]) -> None:
        # Idempotent upsert based on _id
        try:
            _id = doc.get("_id")
            self.collection.update_one({"_id": _id}, {"$set": doc}, upsert=True)
        except Exception as e:
            raise ResearchAnalystException(f"Astra upsert failed for {_id}: {e}")


class MultiIngestion:
    def __init__(self, data_dir: Optional[str] = None) -> None:
        cfg = get_config()
        conf_dir = ((cfg.get("ingestion") or {}).get("data_dir") or "datafolder")
        resolved_dir = data_dir or os.getenv("DATA_DIR") or conf_dir
        self.data_dir = Path(resolved_dir)
        if not self.data_dir.exists():
            raise ResearchAnalystException(f"Data folder not found: {self.data_dir}")
        coll_name = (cfg.get("astra_db") or {}).get("collection_name") or "documents"
        self.astra = AstraClient(coll_name)
        # Embedding backend via ModelLoader (env/config driven)
        self.embedder = ModelLoader(cfg).load_embeddings()["embed"]

    def iter_files(self) -> Iterable[Path]:
        for fp in sorted(self.data_dir.rglob("*")):
            if fp.is_file():
                yield fp

    def process_file(self, fp: Path) -> Dict[str, Any]:
        try:
            text = extract_text_any(fp)
            pieces = chunk_text(text)
            if not pieces:
                logger.warning("No chunks created", file=str(fp))
                return {"file": str(fp), "chunks": 0, "upserts": 0}

            upserts = 0
            for idx, piece in enumerate(pieces):
                _id = sha1_hex(f"{fp.as_posix()}::{idx}::{len(piece)}")
                vec = self.embedder(piece)
                doc = {
                    "_id": _id,
                    "text": piece,
                    "metadata": {
                        "source": fp.as_posix(),
                        "chunk_index": idx,
                        "total_len": len(text),
                        "filename": fp.name,
                    },
                    "embedding": vec,
                }
                self.astra.upsert_chunk(doc)
                upserts += 1

            logger.info("File processed", file=str(fp), chunks=len(pieces), upserts=upserts)
            return {"file": str(fp), "chunks": len(pieces), "upserts": upserts}
        except Exception as e:
            logger.error("File failed", file=str(fp), error=str(e))
            return {"file": str(fp), "error": str(e)}

    def run(self) -> Dict[str, Any]:
        results = {"processed": 0, "failed": 0, "total_chunks": 0, "total_upserts": 0}
        for fp in self.iter_files():
            info = self.process_file(fp)
            if "error" in info:
                results["failed"] += 1
            else:
                results["processed"] += 1
                results["total_chunks"] += info.get("chunks", 0)
                results["total_upserts"] += info.get("upserts", 0)
        logger.info("Multi-ingestion complete", **results)
        return results


def main() -> None:
    try:
        data_dir = os.getenv("DATA_DIR") or (sys.argv[1] if len(sys.argv) > 1 else "datafolder")
        runner = MultiIngestion(data_dir)
        res = runner.run()
        print(f"✅ Processed: {res['processed']} | ❌ Failed: {res['failed']} | 📊 Chunks: {res['total_chunks']} | ⬆️ Upserts: {res['total_upserts']}")
    except Exception as e:
        logger.error("Multi-ingestion failed", error=str(e))
        print(f"❌ Multi-ingestion failed: {e}")


if __name__ == "__main__":
    main()


