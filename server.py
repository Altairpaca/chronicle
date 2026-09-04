from __future__ import annotations

import json
import argparse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable
from urllib.parse import parse_qs, urlparse

from ledger import LedgerStore

ROOT = Path(__file__).parent
STATIC_ROOT = ROOT / "static"
MAX_JSON_BODY_BYTES = 64 * 1024


class ChronicleHandler(SimpleHTTPRequestHandler):
    store: LedgerStore

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, directory=str(STATIC_ROOT), **kwargs)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/summary":
            date_value = parse_qs(parsed.query).get("date", [""])[0]
            self._respond_json(HTTPStatus.OK, self.store.daily_summary(date_value))
            return
        if parsed.path == "/healthz":
            self._respond_json(HTTPStatus.OK, {"status": "ok"})
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        handlers: dict[str, Callable[[dict[str, object]], dict[str, object]]] = {
            "/api/entries": self._create_entry,
            "/api/plans": self._create_plan,
        }
        handler = handlers.get(parsed.path)
        if handler is None:
            self._respond_json(HTTPStatus.NOT_FOUND, {"error": "找不到接口"})
            return
        try:
            self._respond_json(HTTPStatus.CREATED, handler(self._read_json()))
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            self._respond_json(HTTPStatus.BAD_REQUEST, {"error": str(error)})

    def _create_entry(self, payload: dict[str, object]) -> dict[str, object]:
        return self.store.create_entry(
            self._text(payload, "title"), self._text(payload, "started_at"), self._text(payload, "ended_at"),
            self._text(payload, "category"), self._bs_mode(payload), self._integer(payload, "energy"), self._text(payload, "note"),
        )

    def _create_plan(self, payload: dict[str, object]) -> dict[str, object]:
        return self.store.create_plan(self._text(payload, "title"), self._text(payload, "planned_date"), self._integer(payload, "target_minutes"), self._text(payload, "category"))

    def _read_json(self) -> dict[str, object]:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 0 or length > MAX_JSON_BODY_BYTES:
            raise ValueError(f"请求体不得超过 {MAX_JSON_BODY_BYTES} 字节")
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("请求体必须是对象")
        return payload

    def _text(self, payload: dict[str, object], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str):
            raise ValueError(f"{key} 必须是文本")
        return value

    def _integer(self, payload: dict[str, object], key: str) -> int:
        value = payload.get(key)
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{key} 必须是整数")
        return value

    def _bs_mode(self, payload: dict[str, object]) -> str:
        mode = self._text(payload, "bs_mode")
        if mode not in ("B", "S"):
            raise ValueError("bs_mode 必须为 B 或 S")
        return mode

    def _respond_json(self, status: HTTPStatus, payload: dict[str, object]) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def end_headers(self) -> None:
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


def run(host: str = "127.0.0.1", port: int = 8787, database_path: Path = ROOT / "data" / "chronicle.sqlite3") -> None:
    ChronicleHandler.store = LedgerStore(database_path)
    with ThreadingHTTPServer((host, port), ChronicleHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chronicle personal time ledger")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8787, type=int)
    parser.add_argument("--database", default=str(ROOT / "data" / "chronicle.sqlite3"))
    arguments = parser.parse_args()
    run(arguments.host, arguments.port, Path(arguments.database))
