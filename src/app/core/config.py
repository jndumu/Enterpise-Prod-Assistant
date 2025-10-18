from pathlib import Path
import os
import yaml
from dotenv import load_dotenv

from src.core.logging.custom_logger import CustomLogger
from src.core.exceptions.custom_exception import ResearchAnalystException


_log = CustomLogger().get_logger(__name__)
_CONFIG_CACHE: dict | None = None


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_env(env_path: str | None = None) -> None:
    if env_path:
        load_dotenv(dotenv_path=env_path, override=False)
    else:
        load_dotenv(override=False)


def get_config(config_path: str | None = None) -> dict:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    try:
        chosen = config_path or os.getenv("CONFIG_PATH") or str(_project_root() / "config" / "config.yaml")
        path = Path(chosen)
        if not path.is_absolute():
            path = _project_root() / path
        if not path.exists():
            _log.error("config_missing", path=str(path))
            raise FileNotFoundError(f"Config file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        _CONFIG_CACHE = data
        _log.info("config_loaded", path=str(path))
        return data
    except yaml.YAMLError as e:
        _log.error("config_parse_error", error=str(e))
        raise ResearchAnalystException(f"Failed to parse config: {e}") from e
    except Exception as e:
        _log.error("config_load_error", error=str(e))
        raise ResearchAnalystException("Unexpected error loading config") from e


def require_env(name: str) -> str:
    val = os.getenv(name)
    if not val:
        raise ResearchAnalystException(f"Missing required environment variable: {name}")
    return val

