"""File payload decoding utilities."""

from __future__ import annotations

import base64
import io
import json
import zipfile
from html import unescape
from pathlib import Path
from xml.etree import ElementTree


def _decode_bytes(data_base64: str) -> bytes:
    if "," in data_base64 and data_base64.startswith("data:"):
        data_base64 = data_base64.split(",", 1)[1]
    return base64.b64decode(data_base64)


def extract_docx_text(raw: bytes) -> str:
    paragraphs: list[str] = []
    with zipfile.ZipFile(io.BytesIO(raw)) as docx:
        xml = docx.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    for paragraph in root.findall(".//w:p", ns):
        texts = [node.text or "" for node in paragraph.findall(".//w:t", ns)]
        value = "".join(texts).strip()
        if value:
            paragraphs.append(value)
    return "\n".join(paragraphs)


def extract_text_from_payload(filename: str, payload: dict[str, object]) -> str:
    filename = filename or "untitled.txt"
    suffix = Path(filename).suffix.lower()
    if payload.get("text"):
        return str(payload["text"])
    data_base64 = str(payload.get("data_base64") or "")
    if not data_base64:
        return ""
    raw = _decode_bytes(data_base64)
    if suffix == ".docx":
        return extract_docx_text(raw)
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        text = raw.decode("utf-8", errors="ignore")
    if suffix == ".json":
        try:
            parsed = json.loads(text)
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return text
    return unescape(text)
