"""Knowledge graph, corpus ingestion, and 2-hop retrieval services."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .chunking import chunk_text
from .embedding import HashingEmbedder, concept_hits, cosine_similarity
from .storage import Store


MICRO_INTENT_ALIASES = {
    "py_K003": ["print", "打印", "输出"],
    "py_K008": ["缩进", "indent", "indentation"],
    "py_K011": ["变量", "变量概念"],
    "py_K014": ["赋值", "等号", "="],
    "py_K018": ["字符串", "str", "文本"],
    "py_K025": ["input", "输入"],
    "py_K034": ["and", "逻辑与"],
    "py_K035": ["or", "逻辑或"],
    "py_K052": ["if", "条件", "分支"],
    "py_K059": ["while", "循环条件"],
    "py_K062": ["for", "遍历", "循环列表"],
    "py_K063": ["range", "循环次数"],
    "py_K072": ["列表", "list", "数组"],
    "py_K074": ["列表索引", "list[0]", "下标"],
    "py_K087": ["列表推导", "推导式"],
    "py_K090": ["字典", "dict"],
    "py_K098": ["import", "导包"],
    "py_K108": ["def", "函数", "自定义函数"],
    "py_K112": ["return", "返回值"],
    "py_K122": ["traceback", "报错行号"],
    "py_K124": ["syntaxerror", "语法错误"],
    "py_K125": ["indentationerror", "缩进错误"],
    "py_K126": ["nameerror", "未定义", "变量未定义"],
    "py_K127": ["typeerror", "类型错误", "类型转换"],
    "py_K128": ["valueerror", "值错误", "强转"],
    "py_K129": ["indexerror", "越界", "下标越界", "索引越界", "列表越界"],
    "py_K130": ["keyerror", "键错误"],
    "py_K132": ["zerodivisionerror", "除数为零"],
    "py_K133": ["死循环", "卡死"],
}


class KnowledgeGraphService:
    def __init__(self, store: Store, embedder: HashingEmbedder | None = None) -> None:
        self.store = store
        self.embedder = embedder or HashingEmbedder()

    def ingest_document(self, filename: str, text: str, source_type: str = "upload") -> dict[str, Any]:
        title = Path(filename).stem or filename
        chunks = chunk_text(text)
        document_id = self.store.create_document(filename, title, source_type, text)
        doc_node = f"doc:{document_id}"
        self.store.upsert_node(
            id=doc_node,
            label=title[:42],
            kind="document",
            description=f"上传材料：{filename}，已切分为 {len(chunks)} 条相关知识。",
            mastery=0.5,
            meta={"filename": filename, "document_id": document_id},
        )

        created_chunks: list[dict[str, Any]] = []
        for index, chunk in enumerate(chunks):
            embedding = self.embedder.embed(chunk)
            summary = self._summarize(chunk)
            chunk_id = self.store.create_chunk(document_id, index, chunk, embedding, summary)
            chunk_node = f"chunk:{chunk_id}"
            self.store.upsert_node(
                id=chunk_node,
                label=f"{title[:18]} #{index + 1}",
                kind="chunk",
                description=summary,
                mastery=0.5,
                meta={"chunk_id": chunk_id, "document_id": document_id},
            )
            self.store.upsert_edge(doc_node, chunk_node, "HAS_CHUNK", 1.0)
            for concept_id, score in concept_hits(chunk)[:6]:
                self.store.upsert_edge(chunk_node, concept_id, "MENTIONS", min(1.0, 0.35 + score * 0.15))
            created_chunks.append({"id": chunk_id, "index": index, "summary": summary})
        self.store.conn.commit()
        return {
            "document_id": document_id,
            "filename": filename,
            "chunks": len(chunks),
            "created_chunks": created_chunks,
        }

    def retrieve(self, query: str, hop: int = 2, low_doc_limit: int = 3) -> dict[str, Any]:
        query_embedding = self.embedder.embed(query)
        chunk_rows = self.store.rows(
            """
            SELECT c.id, c.document_id, c.chunk_index, c.text, c.embedding, c.summary, d.filename, d.title
            FROM chunks c
            JOIN documents d ON d.id = c.document_id
            ORDER BY c.id DESC
            """
        )
        scored_chunks: list[dict[str, Any]] = []
        for row in chunk_rows:
            score = cosine_similarity(query_embedding, row["embedding"])
            if score > 0.02:
                row["score"] = round(score, 4)
                row["text_preview"] = self._preview(row["text"])
                scored_chunks.append(row)
        scored_chunks.sort(key=lambda item: item["score"], reverse=True)
        evidence_chunks = scored_chunks[:low_doc_limit]

        target_micro_concept = self.map_intent_to_micro_concept(query)
        seed_ids = {node_id for node_id, _ in concept_hits(query)[:8]}
        if target_micro_concept:
            seed_ids.add(target_micro_concept["id"])
            seed_ids.add("student_intermediate_graph")
            for edge in self.store.rows(
                "SELECT target FROM edges WHERE source=? AND relation='REQUIRES'",
                (target_micro_concept["id"],),
            ):
                seed_ids.add(edge["target"])
        for chunk in evidence_chunks:
            chunk_node = f"chunk:{chunk['id']}"
            seed_ids.add(chunk_node)
            for edge in self.store.rows("SELECT target FROM edges WHERE source=? AND relation='MENTIONS'", (chunk_node,)):
                seed_ids.add(edge["target"])
        if not seed_ids:
            seed_ids.add("system_ct_graphmas")
            seed_ids.add("strategy_2hop")

        subgraph = self.expand_subgraph(seed_ids, hop=hop)
        return {
            "strategy": {
                "hop": hop,
                "doc_policy": "RouteEvidence",
                "chunk_limit": low_doc_limit,
                "rationale": "按当前路由节点选择必要图谱关系和少量高相关知识，避免完整图谱造成认知负荷。",
            },
            "seed_ids": sorted(seed_ids),
            "target_micro_concept": target_micro_concept,
            "kg_state": self.get_2_hop_context(target_micro_concept["id"]) if target_micro_concept else "未映射到明确的 145 节点微观考点。",
            "evidence_chunks": evidence_chunks,
            "subgraph": subgraph,
        }

    def map_intent_to_micro_concept(self, query: str) -> dict[str, Any] | None:
        """Map a learner utterance to the nearest K001-K145 micro concept."""
        rows = self.store.rows(
            "SELECT id, label, kind, description, mastery, meta FROM nodes WHERE kind='micro_concept'"
        )
        if not rows:
            return None
        lowered = query.lower()
        explicit = re.search(r"\bK\d{3}\b", query, flags=re.IGNORECASE)
        if explicit:
            target_id = f"py_{explicit.group(0).upper()}"
            for row in rows:
                if row["id"] == target_id:
                    return self._micro_concept_payload(row, score=100)

        scored: list[tuple[float, dict[str, Any]]] = []
        for row in rows:
            meta = row.get("meta") or {}
            concept_id = str(meta.get("concept_id") or row["id"].removeprefix("py_"))
            label = str(row.get("label") or "")
            description = str(row.get("description") or "")
            score = 0.0
            if label and label.lower() in lowered:
                score += 8.0
            if description and description.lower() in lowered:
                score += 5.0
            for alias in MICRO_INTENT_ALIASES.get(row["id"], []):
                if alias.lower() in lowered:
                    score += 10.0 if len(alias) >= 4 else 5.0
            for token in self._concept_tokens(label, description, concept_id):
                if token.lower() in lowered:
                    score += 1.8 if len(token) >= 3 else 1.0
            if score > 0:
                scored.append((score, row))
        if not scored:
            return None
        scored.sort(key=lambda item: (item[0], item[1].get("mastery") or 0), reverse=True)
        return self._micro_concept_payload(scored[0][1], score=round(scored[0][0], 2))

    def get_2_hop_context(self, target_node_id: str) -> str:
        target = self.store.row(
            "SELECT id, label, kind, description, mastery, meta FROM nodes WHERE id=?",
            (target_node_id,),
        )
        if not target:
            return "无当前考点的图谱学情记录。"
        know_edge = self.store.row(
            """
            SELECT source, target, relation, weight, meta
            FROM edges
            WHERE source='student_intermediate_graph' AND target=? AND relation='KNOWS'
            """,
            (target_node_id,),
        )
        target_meta = target.get("meta") or {}
        mastery = know_edge.get("meta", {}).get("mastery_level") if know_edge else target.get("mastery")
        status = know_edge.get("meta", {}).get("status") if know_edge else "Learning"
        lines = [
            f"核心考点: 【{target_meta.get('concept_id', target_node_id)} {target['label']}】",
            f"考点说明: {target.get('description') or '无'}",
            f"建构期中等生掌握度: {mastery}，状态: {status}",
        ]
        prereq_edges = self.store.rows(
            """
            SELECT e.target AS node_id, n.label, n.description, n.meta, k.meta AS knows_meta, k.weight AS mastery
            FROM edges e
            JOIN nodes n ON n.id=e.target
            LEFT JOIN edges k
              ON k.source='student_intermediate_graph'
             AND k.target=e.target
             AND k.relation='KNOWS'
            WHERE e.source=? AND e.relation='REQUIRES'
            ORDER BY n.label
            """,
            (target_node_id,),
        )
        if prereq_edges:
            lines.append("前置知识点:")
            for edge in prereq_edges:
                knows_meta = edge.get("knows_meta") or {}
                if isinstance(knows_meta, str):
                    try:
                        knows_meta = json.loads(knows_meta)
                    except json.JSONDecodeError:
                        knows_meta = {}
                cid = (edge.get("meta") or {}).get("concept_id") or edge["node_id"].removeprefix("py_")
                level = knows_meta.get("mastery_level", edge.get("mastery", 0))
                edge_status = knows_meta.get("status", "Learning")
                lines.append(f" - {cid} {edge['label']} (掌握度: {level}, 状态: {edge_status})")
        else:
            lines.append("前置知识点: 当前节点暂无显式 REQUIRES 前置边。")
        return "\n".join(lines)

    @staticmethod
    def _concept_tokens(label: str, description: str, concept_id: str) -> list[str]:
        text = f"{concept_id} {label} {description}"
        tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*|\d+(?:\.\d+)?", text)
        for run in re.findall(r"[\u4e00-\u9fff]{2,}", text):
            if len(run) <= 4:
                tokens.append(run)
            else:
                tokens.extend(run[i : i + 2] for i in range(len(run) - 1))
                tokens.extend(run[i : i + 3] for i in range(len(run) - 2))
        return list(dict.fromkeys(tokens))

    @staticmethod
    def _micro_concept_payload(row: dict[str, Any], score: float) -> dict[str, Any]:
        meta = row.get("meta") or {}
        return {
            "id": row["id"],
            "concept_id": meta.get("concept_id", row["id"].removeprefix("py_")),
            "label": row["label"],
            "description": row.get("description") or "",
            "stage": meta.get("stage"),
            "mastery": row.get("mastery"),
            "score": score,
        }

    def expand_subgraph(self, seed_ids: set[str], hop: int = 2) -> dict[str, list[dict[str, Any]]]:
        frontier = set(seed_ids)
        visited = set(seed_ids)
        edges: list[dict[str, Any]] = []
        for _ in range(max(0, hop)):
            if not frontier:
                break
            placeholders = ",".join("?" for _ in frontier)
            rows = self.store.rows(
                f"""
                SELECT source, target, relation, weight, meta
                FROM edges
                WHERE source IN ({placeholders}) OR target IN ({placeholders})
                """,
                tuple(frontier) + tuple(frontier),
            )
            next_frontier: set[str] = set()
            for edge in rows:
                edge_key = (edge["source"], edge["target"], edge["relation"])
                if not any((item["source"], item["target"], item["relation"]) == edge_key for item in edges):
                    edges.append(edge)
                for endpoint in (edge["source"], edge["target"]):
                    if endpoint not in visited:
                        visited.add(endpoint)
                        next_frontier.add(endpoint)
            frontier = next_frontier

        if not visited:
            return {"nodes": [], "edges": []}
        placeholders = ",".join("?" for _ in visited)
        nodes = self.store.rows(
            f"SELECT id, label, kind, description, mastery, meta FROM nodes WHERE id IN ({placeholders})",
            tuple(visited),
        )
        nodes.sort(key=lambda node: (0 if node["id"] in seed_ids else 1, node["kind"], node["label"]))
        return {"nodes": nodes[:80], "edges": edges[:140]}

    def corpus_overview(self) -> dict[str, Any]:
        docs = self.store.rows(
            """
            SELECT d.id, d.filename, d.title, d.source_type, d.created_at, COUNT(c.id) AS chunks
            FROM documents d
            LEFT JOIN chunks c ON c.document_id = d.id
            GROUP BY d.id
            ORDER BY d.id DESC
            """
        )
        return {
            "documents": docs,
            "chunk_count": self.store.scalar("SELECT COUNT(*) FROM chunks") or 0,
            "node_count": self.store.scalar("SELECT COUNT(*) FROM nodes") or 0,
            "edge_count": self.store.scalar("SELECT COUNT(*) FROM edges") or 0,
        }

    @staticmethod
    def _summarize(text: str, limit: int = 90) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        return text if len(text) <= limit else text[: limit - 1] + "…"

    @staticmethod
    def _preview(text: str, limit: int = 260) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        return text if len(text) <= limit else text[: limit - 1] + "…"

    def node_label(self, node_id: str) -> str:
        row = self.store.row("SELECT label FROM nodes WHERE id=?", (node_id,))
        return row["label"] if row else node_id

    def graph_json(self) -> str:
        return json.dumps(self.store.graph(), ensure_ascii=False)
