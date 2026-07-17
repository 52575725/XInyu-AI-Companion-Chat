"""Runtime configuration and process-wide infrastructure for the demo backend."""

from __future__ import annotations

import os
import time
from pathlib import Path
from threading import BoundedSemaphore, Lock


ROOT = Path(__file__).resolve().parent


def load_dotenv() -> None:
    path = ROOT / ".env"
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    return max(minimum, min(value, maximum))


load_dotenv()

HOST = os.getenv("APP_HOST", "127.0.0.1").strip() or "127.0.0.1"
PORT = env_int("APP_PORT", 8080, 1, 65535)
AI_API_KEY = os.getenv("AI_API_KEY", "").strip()
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://api.deepseek.com").strip().rstrip("/")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-chat").strip()
AI_TIMEOUT = env_int("AI_TIMEOUT", 12, 3, 12)
MODEL_CONCURRENCY = env_int("MODEL_CONCURRENCY", 3, 1, 8)
REQUEST_LOG = ROOT / "request.log"
REQUEST_LOG_MAX_BYTES = env_int("REQUEST_LOG_MAX_BYTES", 2_000_000, 100_000, 20_000_000)
APP_VERSION = "2026.07.17.2"
PID_FILE = ROOT / "server.pid"
MODEL_SLOTS = BoundedSemaphore(MODEL_CONCURRENCY)
LOG_LOCK = Lock()


def log_event(message: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with LOG_LOCK:
        try:
            if REQUEST_LOG.exists() and REQUEST_LOG.stat().st_size >= REQUEST_LOG_MAX_BYTES:
                rotated = REQUEST_LOG.with_suffix(".log.1")
                if rotated.exists():
                    rotated.unlink()
                REQUEST_LOG.replace(rotated)
        except OSError:
            pass
        with REQUEST_LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"[{stamp}] {message}\n")
