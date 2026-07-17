"""Static asset and JSON API transport for the local demo."""

from __future__ import annotations

import json
import os
import socket
import sys
import urllib.parse
import webbrowser
from collections.abc import Callable
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import BoundedSemaphore, Timer
from typing import Any


def is_allowed_static_path(path: str) -> bool:
    clean = urllib.parse.unquote(path.split("?", 1)[0]).replace("\\", "/")
    if ".." in clean.split("/"):
        return False
    if clean in {"/", "/index.html", "/app.js", "/characters.js", "/styles.css"}:
        return True
    if not clean.startswith("/assets/"):
        return False
    return Path(clean).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}


def create_handler(
    *,
    root: Path,
    chat: Callable[[dict[str, Any]], dict[str, Any]],
    status: Callable[[], dict[str, Any]],
    logger: Callable[[str], None],
    model_slots: BoundedSemaphore,
) -> type[SimpleHTTPRequestHandler]:
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, directory=str(root), **kwargs)

        def send_json(self, status_code: int, data: dict[str, Any]) -> None:
            encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

        def end_headers(self) -> None:
            if not self.path.startswith("/api/"):
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
            super().end_headers()

        def clean_request_path(self) -> str:
            return urllib.parse.unquote(self.path.split("?", 1)[0]).replace("\\", "/")

        def do_GET(self) -> None:  # noqa: N802
            clean_path = self.clean_request_path()
            if clean_path != "/api/status" and not is_allowed_static_path(clean_path):
                self.send_error(404)
                return
            if clean_path == "/api/status":
                self.send_json(200, status())
                return
            super().do_GET()

        def do_HEAD(self) -> None:  # noqa: N802
            if not is_allowed_static_path(self.clean_request_path()):
                self.send_error(404)
                return
            super().do_HEAD()

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/api/chat":
                self.send_json(404, {"error": "接口不存在"})
                return
            try:
                logger(f"POST received path={self.path} content_length={self.headers.get('Content-Length', '')}")
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 1_000_000:
                    raise ValueError("请求内容为空或过大")
                self.connection.settimeout(15)
                raw = self.rfile.read(length)
                logger(f"POST body read bytes={len(raw)} expected={length}")
                if len(raw) != length:
                    raise ValueError("请求内容传输不完整")
                data = json.loads(raw.decode("utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("请求格式错误")
                if not model_slots.acquire(blocking=False):
                    logger("chat rejected: model concurrency limit reached")
                    self.send_json(503, {"error": "当前请求较多，请稍后再试。"})
                    return
                try:
                    result = chat(data)
                finally:
                    model_slots.release()
                self.send_json(200, result)
            except socket.timeout:
                logger("POST body timeout")
                self.send_json(408, {"error": "本地请求读取超时，请重新发送。"})
            except (ValueError, RuntimeError) as exc:
                logger(f"chat error: {exc}")
                self.send_json(400, {"error": str(exc)})
            except Exception as exc:
                print(f"Unexpected error: {exc}", file=sys.stderr)
                self.send_json(500, {"error": "服务处理失败，请查看终端日志。"})

    return Handler


def serve_demo(
    *,
    host: str,
    port: int,
    handler: type[SimpleHTTPRequestHandler],
    pid_file: Path,
    model: str,
    configured: bool,
) -> None:
    try:
        server = ThreadingHTTPServer((host, port), handler)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 10048 or getattr(exc, "errno", None) == 10048:
            print(f"端口 {port} 已被占用。Demo 可能已经启动，请访问 http://{host}:{port}")
            webbrowser.open(f"http://{host}:{port}")
            raise SystemExit(0) from exc
        raise

    print(f"心语 Demo 已启动：http://{host}:{port}")
    print(f"模型：{model} | 配置状态：{'已配置' if configured else '缺少 AI_API_KEY'}")
    pid_file.write_text(str(os.getpid()), encoding="ascii")
    if os.getenv("APP_OPEN_BROWSER", "1") == "1" and "--no-browser" not in sys.argv:
        Timer(0.8, lambda: webbrowser.open(f"http://{host}:{port}")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")
    finally:
        try:
            if pid_file.exists() and pid_file.read_text(encoding="ascii").strip() == str(os.getpid()):
                pid_file.unlink()
        except OSError:
            pass
