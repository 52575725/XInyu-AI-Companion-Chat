"""Executable entry point for the Heart Talk demo backend."""

from __future__ import annotations

from backend_config import AI_API_KEY, AI_MODEL, HOST, PID_FILE, PORT
from conversation_engine import *  # noqa: F403 - preserve the original import surface
from conversation_engine import Handler
from http_app import serve_demo


if __name__ == "__main__":
    serve_demo(
        host=HOST,
        port=PORT,
        handler=Handler,
        pid_file=PID_FILE,
        model=AI_MODEL,
        configured=bool(AI_API_KEY),
    )
