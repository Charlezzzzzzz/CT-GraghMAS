"""CT-GraphMAS local web application.

Run:
    python3 main.py --port 8877
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import secrets
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from ct_graphmas.agents import CTGraphMAS
from ct_graphmas.knowledge_graph import KnowledgeGraphService
from ct_graphmas.prompt_workflow import prompt_workflow_payload
from ct_graphmas.storage import Store
from ct_graphmas.textutils import extract_text_from_payload
from ct_graphmas.theory import theory_payload


ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
DATA = ROOT / "data"


class AppContext:
    def __init__(self, db_path: Path) -> None:
        self.store = Store(db_path)
        self.kg = KnowledgeGraphService(self.store)
        self.mas = CTGraphMAS(self.store, self.kg)
        self.sessions: dict[str, dict[str, object]] = {}


def make_handler(ctx: AppContext):
    class Handler(BaseHTTPRequestHandler):
        server_version = "CTGraphMAS/0.1"

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in {"/", "/index.html"}:
                return self._send_file(STATIC / "index.html")
            if parsed.path.startswith("/static/"):
                rel = parsed.path.removeprefix("/static/")
                return self._send_file(STATIC / rel)
            if parsed.path == "/api/graph":
                return self._json(ctx.store.graph())
            if parsed.path == "/api/corpus":
                return self._json(ctx.kg.corpus_overview())
            if parsed.path == "/api/interactions":
                query = parse_qs(parsed.query)
                limit = int(query.get("limit", ["10"])[0])
                rows = ctx.store.rows(
                    """
                    SELECT id, created_at, student_profile, workflow, style, user_message,
                           diagnosis_json, answer_json, gate_json
                    FROM interactions
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                )
                return self._json({"interactions": rows})
            if parsed.path == "/api/session":
                user = self._current_user()
                return self._json({"user": user})
            if parsed.path == "/api/dashboard":
                return self._json(ctx.store.dashboard())
            if parsed.path == "/api/users":
                return self._json({"users": ctx.store.users()})
            if parsed.path == "/api/tasks":
                return self._json({"tasks": ctx.store.tasks()})
            if parsed.path == "/api/theory":
                return self._json(theory_payload())
            if parsed.path == "/api/prompt-workflow":
                return self._json(prompt_workflow_payload())
            if parsed.path == "/api/settings":
                return self._json({"settings": ctx.store.api_settings(mask_key=True)})
            return self._not_found()

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/api/login":
                payload = self._read_json()
                username = str(payload.get("username") or "").strip()
                password = str(payload.get("password") or "")
                user = ctx.store.authenticate_user(username, password)
                if not user:
                    return self._json({"error": "用户名或密码不正确"}, status=401)
                token = secrets.token_urlsafe(24)
                ctx.sessions[token] = user
                return self._json({"token": token, "user": user, "navigation": self._navigation_for(user)})
            if parsed.path == "/api/logout":
                token = self._bearer_token()
                if token:
                    ctx.sessions.pop(token, None)
                return self._json({"ok": True})
            if parsed.path == "/api/settings":
                user = self._current_user()
                if not user:
                    return self._json({"error": "请先登录后再保存设置"}, status=403)
                payload = self._read_json()
                return self._json({"settings": ctx.store.update_api_settings(payload)})
            if parsed.path == "/api/tasks":
                user = self._current_user()
                if not user or user.get("role") not in {"teacher", "admin"}:
                    return self._json({"error": "只有教师或管理员可以分配班级任务"}, status=403)
                payload = self._read_json()
                try:
                    task = ctx.store.create_task(payload, user)
                except ValueError as exc:
                    return self._json({"error": str(exc)}, status=400)
                return self._json({"task": task, "tasks": ctx.store.tasks()})
            if parsed.path == "/api/chat":
                payload = self._read_json()
                message = str(payload.get("message") or "").strip()
                if not message:
                    return self._json({"error": "message is required"}, status=400)
                result = ctx.mas.respond(
                    message=message,
                    profile=str(payload.get("profile") or "intermediate"),
                    style=str(payload.get("style") or "tutor"),
                    workflow=str(payload.get("workflow") or "coder"),
                    mode=str(payload.get("mode") or "teaching"),
                )
                return self._json(result)
            if parsed.path == "/api/upload":
                payload = self._read_json()
                filename = str(payload.get("filename") or "uploaded.txt")
                text = extract_text_from_payload(filename, payload)
                if not text.strip():
                    return self._json({"error": "empty corpus text"}, status=400)
                result = ctx.kg.ingest_document(filename, text, source_type="upload")
                return self._json(result)
            return self._not_found()

        def _read_json(self) -> dict[str, object]:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length else b"{}"
            try:
                return json.loads(body.decode("utf-8"))
            except json.JSONDecodeError:
                return {}

        def _json(self, data: object, status: int = 200) -> None:
            raw = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _send_file(self, path: Path) -> None:
            path = path.resolve()
            if not str(path).startswith(str(STATIC.resolve())) or not path.exists() or not path.is_file():
                return self._not_found()
            content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
            raw = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _not_found(self) -> None:
            self._json({"error": "not found"}, status=404)

        def _bearer_token(self) -> str | None:
            header = self.headers.get("Authorization", "")
            if header.startswith("Bearer "):
                return header.removeprefix("Bearer ").strip()
            return None

        def _current_user(self) -> dict[str, object] | None:
            token = self._bearer_token()
            if not token:
                return None
            return ctx.sessions.get(token)

        @staticmethod
        def _navigation_for(user: dict[str, object]) -> list[dict[str, str]]:
            role = user.get("role")
            if role == "admin":
                return [
                    {"id": "home", "label": "系统总览"},
                    {"id": "admin", "label": "管理中心"},
                    {"id": "settings", "label": "设置页面"},
                    {"id": "teacher", "label": "教师视图"},
                    {"id": "knowledge", "label": "知识库"},
                    {"id": "graph", "label": "知识图谱"},
                    {"id": "corpus", "label": "语料库"},
                ]
            if role == "teacher":
                return [
                    {"id": "home", "label": "班级总览"},
                    {"id": "teacher", "label": "教师工作台"},
                    {"id": "daily", "label": "通用答疑"},
                    {"id": "teaching", "label": "教学伴学"},
                    {"id": "knowledge", "label": "知识库"},
                    {"id": "graph", "label": "知识图谱"},
                    {"id": "corpus", "label": "语料库"},
                    {"id": "settings", "label": "设置页面"},
                ]
            return [
                {"id": "home", "label": "我的首页"},
                {"id": "daily", "label": "日常答疑"},
                {"id": "teaching", "label": "教学伴学"},
                {"id": "knowledge", "label": "知识库"},
                {"id": "graph", "label": "我的图谱"},
                {"id": "settings", "label": "设置页面"},
            ]

        def log_message(self, fmt: str, *args: object) -> None:
            print(f"[CT-GraphMAS] {self.address_string()} - {fmt % args}")

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the CT-GraphMAS local web app.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8877)
    parser.add_argument("--db", default=str(DATA / "ct_graphmas.sqlite3"))
    args = parser.parse_args()

    ctx = AppContext(Path(args.db))
    server = ThreadingHTTPServer((args.host, args.port), make_handler(ctx))
    print(f"CT-GraphMAS is running at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down CT-GraphMAS.")
    finally:
        ctx.store.close()
        server.server_close()


if __name__ == "__main__":
    main()
