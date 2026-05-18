"""SQLite storage layer for CT-GraphMAS."""

from __future__ import annotations

import json
import hashlib
import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

from .seed_data import SEED_EDGES, SEED_NODES


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def password_hash(password: str) -> str:
    return hashlib.sha256(f"ct-graphmas::{password}".encode("utf-8")).hexdigest()


class Store:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.initialize()

    def initialize(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                title TEXT,
                source_type TEXT,
                raw_text TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                chunk_index INTEGER NOT NULL,
                text TEXT NOT NULL,
                embedding TEXT NOT NULL,
                summary TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(document_id) REFERENCES documents(id)
            );

            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                label TEXT NOT NULL,
                kind TEXT NOT NULL,
                description TEXT,
                mastery REAL DEFAULT 0.5,
                meta TEXT DEFAULT '{}',
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                target TEXT NOT NULL,
                relation TEXT NOT NULL,
                weight REAL DEFAULT 1.0,
                meta TEXT DEFAULT '{}',
                created_at TEXT NOT NULL,
                UNIQUE(source, target, relation)
            );

            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                student_profile TEXT,
                workflow TEXT,
                style TEXT,
                user_message TEXT NOT NULL,
                diagnosis_json TEXT NOT NULL,
                answer_json TEXT NOT NULL,
                gate_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                display_name TEXT NOT NULL,
                student_no TEXT,
                class_name TEXT,
                profile TEXT,
                avatar TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS learning_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                workflow TEXT NOT NULL,
                target_profile TEXT,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                due_label TEXT,
                class_name TEXT,
                assigned_by TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS api_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                provider TEXT NOT NULL,
                base_url TEXT,
                api_key TEXT,
                chat_model TEXT,
                embedding_model TEXT,
                temperature REAL DEFAULT 0.3,
                enabled INTEGER DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            """
        )
        self.conn.commit()
        self.migrate_schema()
        self.seed_graph()
        if self.scalar("SELECT COUNT(*) FROM users") == 0:
            self.seed_users()
        if self.scalar("SELECT COUNT(*) FROM learning_tasks") == 0:
            self.seed_tasks()
        if self.scalar("SELECT COUNT(*) FROM api_settings") == 0:
            self.seed_api_settings()

    def scalar(self, query: str, params: tuple[Any, ...] = ()) -> Any:
        with self.lock:
            row = self.conn.execute(query, params).fetchone()
        return row[0] if row else None

    def migrate_schema(self) -> None:
        """Keep older local demo databases compatible with the current UI."""
        with self.lock:
            user_columns = {
                row["name"] for row in self.conn.execute("PRAGMA table_info(users)").fetchall()
            }
            if "student_no" not in user_columns:
                self.conn.execute("ALTER TABLE users ADD COLUMN student_no TEXT")

            task_columns = {
                row["name"] for row in self.conn.execute("PRAGMA table_info(learning_tasks)").fetchall()
            }
            if "class_name" not in task_columns:
                self.conn.execute("ALTER TABLE learning_tasks ADD COLUMN class_name TEXT")
            if "assigned_by" not in task_columns:
                self.conn.execute("ALTER TABLE learning_tasks ADD COLUMN assigned_by TEXT")

            self.conn.execute(
                """
                UPDATE users
                SET student_no = CASE
                        WHEN student_no IS NULL OR student_no = '' THEN 'S2025' || printf('%03d', id)
                        ELSE student_no
                    END,
                    display_name = 'L同学'
                WHERE role = 'student'
                """
            )
            self.conn.execute(
                """
                UPDATE learning_tasks
                SET class_name = COALESCE(NULLIF(class_name, ''), '八年级 Python 实验班'),
                    assigned_by = COALESCE(NULLIF(assigned_by, ''), '周老师')
                """
            )
            self.conn.execute(
                """
                UPDATE nodes
                SET description = replace(
                        replace(description, '上传语料：', '上传材料：'),
                        ' 个 chunk',
                        ' 条相关知识'
                    )
                WHERE kind='document'
                """
            )
            self.conn.commit()

    def seed_graph(self) -> None:
        for node in SEED_NODES:
            self.upsert_node(**node)
        for edge in SEED_EDGES:
            self.upsert_edge(**edge)
        self.conn.commit()

    def seed_users(self) -> None:
        users = [
            ("student", "student123", "student", "L同学", "S2025001", "八年级 Python 实验班", "intermediate", "ST"),
            ("teacher", "teacher123", "teacher", "周老师", "", "八年级 Python 实验班", "teacher", "TR"),
            ("admin", "admin123", "admin", "系统管理员", "", "CT-GraphMAS 项目组", "admin", "AD"),
        ]
        for username, password, role, display_name, student_no, class_name, profile, avatar in users:
            self.conn.execute(
                """
                INSERT INTO users(username, password_hash, role, display_name, student_no, class_name, profile, avatar, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (username, password_hash(password), role, display_name, student_no, class_name, profile, avatar, utc_now()),
            )
        self.conn.commit()

    def seed_tasks(self) -> None:
        tasks = [
            (
                "校园活动推荐器",
                "coder",
                "intermediate",
                "围绕真实校园活动完成需求澄清、列表建模、条件筛选、输出推荐和调试复盘。",
                "已分配",
                "本周五",
                "八年级 Python 实验班",
                "周老师",
            ),
            (
                "列表越界调试训练",
                "adapt",
                "novice",
                "通过最小样例、边界样例和变量跟踪理解索引从 0 开始与 len(list) 的关系。",
                "待发布",
                "下节课",
                "八年级 Python 实验班",
                "周老师",
            ),
            (
                "函数封装与迁移挑战",
                "coder",
                "advanced",
                "把一段能运行的过程式代码重构为函数，并说明参数、返回值和复用场景。",
                "草稿",
                "两周内",
                "八年级 Python 实验班",
                "周老师",
            ),
        ]
        for title, workflow, target_profile, description, status, due_label, class_name, assigned_by in tasks:
            self.conn.execute(
                """
                INSERT INTO learning_tasks(
                    title, workflow, target_profile, description, status, due_label,
                    class_name, assigned_by, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, workflow, target_profile, description, status, due_label, class_name, assigned_by, utc_now()),
            )
        self.conn.commit()

    def seed_api_settings(self) -> None:
        with self.lock:
            self.conn.execute(
                """
                INSERT INTO api_settings(
                    id, provider, base_url, api_key, chat_model, embedding_model,
                    temperature, enabled, updated_at
                )
                VALUES(1, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "local-demo",
                    "http://127.0.0.1:11434/v1",
                    "",
                    "local-rule-agent",
                    "hashing-embedding-128",
                    0.3,
                    0,
                    utc_now(),
                ),
            )
            self.conn.commit()

    def upsert_node(
        self,
        id: str,
        label: str,
        kind: str,
        description: str = "",
        mastery: float = 0.5,
        meta: dict[str, Any] | None = None,
    ) -> None:
        with self.lock:
            self.conn.execute(
                """
                INSERT INTO nodes(id, label, kind, description, mastery, meta, created_at)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    label=excluded.label,
                    kind=excluded.kind,
                    description=excluded.description,
                    mastery=excluded.mastery,
                    meta=excluded.meta
                """,
                (id, label, kind, description, mastery, json.dumps(meta or {}, ensure_ascii=False), utc_now()),
            )

    def upsert_edge(
        self,
        source: str,
        target: str,
        relation: str,
        weight: float = 1.0,
        meta: dict[str, Any] | None = None,
    ) -> None:
        with self.lock:
            self.conn.execute(
                """
                INSERT INTO edges(source, target, relation, weight, meta, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                ON CONFLICT(source, target, relation) DO UPDATE SET
                    weight=excluded.weight,
                    meta=excluded.meta
                """,
                (source, target, relation, weight, json.dumps(meta or {}, ensure_ascii=False), utc_now()),
            )

    def create_document(self, filename: str, title: str, source_type: str, raw_text: str) -> int:
        with self.lock:
            cursor = self.conn.execute(
                "INSERT INTO documents(filename, title, source_type, raw_text, created_at) VALUES(?, ?, ?, ?, ?)",
                (filename, title, source_type, raw_text, utc_now()),
            )
            self.conn.commit()
        return int(cursor.lastrowid)

    def create_chunk(self, document_id: int, chunk_index: int, text: str, embedding: list[float], summary: str) -> int:
        with self.lock:
            cursor = self.conn.execute(
                """
                INSERT INTO chunks(document_id, chunk_index, text, embedding, summary, created_at)
                VALUES(?, ?, ?, ?, ?, ?)
                """,
                (document_id, chunk_index, text, json.dumps(embedding), summary, utc_now()),
            )
            self.conn.commit()
        return int(cursor.lastrowid)

    def rows(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.lock:
            rows = self.conn.execute(query, params).fetchall()
        return [self.row_to_dict(row) for row in rows]

    def row(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.lock:
            result = self.conn.execute(query, params).fetchone()
        return self.row_to_dict(result) if result else None

    def authenticate_user(self, username: str, password: str) -> dict[str, Any] | None:
        user = self.row(
            """
            SELECT id, username, role, display_name, student_no, class_name, profile, avatar
            FROM users
            WHERE username=? AND password_hash=?
            """,
            (username, password_hash(password)),
        )
        return user

    def users(self) -> list[dict[str, Any]]:
        return self.rows(
            """
            SELECT id, username, role, display_name, student_no, class_name, profile, avatar, created_at
            FROM users
            ORDER BY CASE role WHEN 'admin' THEN 0 WHEN 'teacher' THEN 1 ELSE 2 END, id
            """
        )

    def tasks(self) -> list[dict[str, Any]]:
        return self.rows(
            """
            SELECT id, title, workflow, target_profile, description, status,
                   due_label, class_name, assigned_by, created_at
            FROM learning_tasks
            ORDER BY id DESC
            """
        )

    def create_task(self, payload: dict[str, Any], user: dict[str, Any]) -> dict[str, Any]:
        title = str(payload.get("title") or "").strip()
        description = str(payload.get("description") or "").strip()
        if not title or not description:
            raise ValueError("任务标题和任务说明不能为空")

        workflow = str(payload.get("workflow") or "coder").strip()
        if workflow not in {"coder", "adapt", "standard"}:
            workflow = "coder"
        target_profile = str(payload.get("target_profile") or "intermediate").strip()
        if target_profile not in {"novice", "intermediate", "advanced"}:
            target_profile = "intermediate"
        status = str(payload.get("status") or "已分配").strip()
        if status not in {"已分配", "进行中", "待发布", "草稿"}:
            status = "已分配"
        due_label = str(payload.get("due_label") or "本周").strip()
        class_name = str(payload.get("class_name") or user.get("class_name") or "默认班级").strip()
        assigned_by = str(user.get("display_name") or user.get("username") or "教师").strip()

        with self.lock:
            cursor = self.conn.execute(
                """
                INSERT INTO learning_tasks(
                    title, workflow, target_profile, description, status, due_label,
                    class_name, assigned_by, created_at
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, workflow, target_profile, description, status, due_label, class_name, assigned_by, utc_now()),
            )
            self.conn.commit()
            task_id = int(cursor.lastrowid)
        return self.row(
            """
            SELECT id, title, workflow, target_profile, description, status,
                   due_label, class_name, assigned_by, created_at
            FROM learning_tasks
            WHERE id=?
            """,
            (task_id,),
        ) or {}

    def dashboard(self) -> dict[str, Any]:
        latest_interactions = self.rows(
            """
            SELECT id, created_at, student_profile, workflow, style, user_message,
                   diagnosis_json, answer_json, gate_json
            FROM interactions
            ORDER BY id DESC
            LIMIT 6
            """
        )
        return {
            "stats": {
                "users": self.scalar("SELECT COUNT(*) FROM users") or 0,
                "tasks": self.scalar("SELECT COUNT(*) FROM learning_tasks") or 0,
                "documents": self.scalar("SELECT COUNT(*) FROM documents") or 0,
                "chunks": self.scalar("SELECT COUNT(*) FROM chunks") or 0,
                "nodes": self.scalar("SELECT COUNT(*) FROM nodes") or 0,
                "edges": self.scalar("SELECT COUNT(*) FROM edges") or 0,
                "interactions": self.scalar("SELECT COUNT(*) FROM interactions") or 0,
            },
            "tasks": self.tasks(),
            "latest_interactions": latest_interactions,
            "mastery": [
                {"label": "问题分解", "value": 0.76, "trend": "+8%"},
                {"label": "抽象建模", "value": 0.62, "trend": "+3%"},
                {"label": "算法设计", "value": 0.69, "trend": "+6%"},
                {"label": "调试评价", "value": 0.81, "trend": "+11%"},
            ],
        }

    def api_settings(self, mask_key: bool = True) -> dict[str, Any]:
        row = self.row(
            """
            SELECT provider, base_url, api_key, chat_model, embedding_model, temperature, enabled, updated_at
            FROM api_settings
            WHERE id=1
            """
        )
        if not row:
            self.seed_api_settings()
            row = self.row(
                """
                SELECT provider, base_url, api_key, chat_model, embedding_model, temperature, enabled, updated_at
                FROM api_settings
                WHERE id=1
                """
            )
        if row and mask_key and row.get("api_key"):
            row["api_key"] = "••••" + str(row["api_key"])[-4:]
        return row or {}

    def update_api_settings(self, payload: dict[str, Any]) -> dict[str, Any]:
        current = self.api_settings(mask_key=False)
        if payload.get("clear_api_key"):
            api_key = ""
        elif "api_key" in payload:
            api_key = str(payload.get("api_key") or "")
        else:
            api_key = str(current.get("api_key") or "")
        if api_key.startswith("••••"):
            api_key = str(current.get("api_key") or "")
        provider = str(payload.get("provider") or current.get("provider") or "openai-compatible")
        base_url = str(payload.get("base_url") or current.get("base_url") or "")
        chat_model = str(payload.get("chat_model") or current.get("chat_model") or "")
        embedding_model = str(payload.get("embedding_model") or current.get("embedding_model") or "")
        try:
            temperature = float(payload.get("temperature", current.get("temperature", 0.3)))
        except (TypeError, ValueError):
            temperature = 0.3
        enabled = 1 if payload.get("enabled") in {True, 1, "1", "true", "on", "yes"} else 0
        with self.lock:
            self.conn.execute(
                """
                UPDATE api_settings
                SET provider=?, base_url=?, api_key=?, chat_model=?, embedding_model=?,
                    temperature=?, enabled=?, updated_at=?
                WHERE id=1
                """,
                (provider, base_url, api_key, chat_model, embedding_model, temperature, enabled, utc_now()),
            )
            self.conn.commit()
        return self.api_settings(mask_key=True)

    @staticmethod
    def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
        value = dict(row)
        for key in ("meta", "embedding", "diagnosis_json", "answer_json", "gate_json"):
            if key in value and isinstance(value[key], str):
                try:
                    value[key] = json.loads(value[key])
                except json.JSONDecodeError:
                    pass
        return value

    def save_interaction(
        self,
        student_profile: str,
        workflow: str,
        style: str,
        user_message: str,
        diagnosis: dict[str, Any],
        answer: dict[str, Any],
        gate: dict[str, Any],
    ) -> int:
        with self.lock:
            cursor = self.conn.execute(
                """
                INSERT INTO interactions(
                    created_at, student_profile, workflow, style, user_message,
                    diagnosis_json, answer_json, gate_json
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now(),
                    student_profile,
                    workflow,
                    style,
                    user_message,
                    json.dumps(diagnosis, ensure_ascii=False),
                    json.dumps(answer, ensure_ascii=False),
                    json.dumps(gate, ensure_ascii=False),
                ),
            )
            self.conn.commit()
        return int(cursor.lastrowid)

    def graph(self, limit: int = 220) -> dict[str, list[dict[str, Any]]]:
        nodes = self.rows(
            """
            SELECT id, label, kind, description, mastery, meta
            FROM nodes
            ORDER BY
                CASE kind
                    WHEN 'system' THEN 0
                    WHEN 'layer' THEN 1
                    WHEN 'agent' THEN 2
                    WHEN 'ct_skill' THEN 3
                    WHEN 'python_concept' THEN 4
                    ELSE 5
                END,
                label
            LIMIT ?
            """,
            (limit,),
        )
        node_ids = {node["id"] for node in nodes}
        edges = [
            edge
            for edge in self.rows("SELECT source, target, relation, weight, meta FROM edges ORDER BY id")
            if edge["source"] in node_ids and edge["target"] in node_ids
        ]
        return {"nodes": nodes, "edges": edges}

    def close(self) -> None:
        with self.lock:
            self.conn.close()
