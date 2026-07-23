import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_DIR = Path(os.getenv("OUTPUT_DIR", str(Path(__file__).parent.parent / "output")))
DB_PATH = DB_DIR / "drafts.db"


def _get_conn() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS drafts (
            id TEXT PRIMARY KEY,
            template_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'draft',
            data TEXT NOT NULL DEFAULT '{}',
            output_filename TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )"""
    )
    return conn


def create_draft(template_name: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    conn = _get_conn()
    try:
        draft_id = uuid.uuid4().hex[:12]
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO drafts (id, template_name, status, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (draft_id, template_name, "draft", json.dumps(data or {}), now, now),
        )
        conn.commit()
        return {"success": True, "draft_id": draft_id}
    finally:
        conn.close()


def update_draft(draft_id: str, data: dict[str, Any]) -> dict[str, Any]:
    conn = _get_conn()
    try:
        row = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if row is None:
            return {"success": False, "error": f"Draft '{draft_id}' not found"}
        merged = {**json.loads(row["data"]), **data}
        now = datetime.now(timezone.utc).isoformat()
        conn.execute("UPDATE drafts SET data = ?, updated_at = ? WHERE id = ?", (json.dumps(merged), now, draft_id))
        conn.commit()
        return {"success": True, "draft_id": draft_id, "data": merged}
    finally:
        conn.close()


def get_draft(draft_id: str) -> dict[str, Any]:
    conn = _get_conn()
    try:
        row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if row is None:
            return {"success": False, "error": f"Draft '{draft_id}' not found"}
        return {
            "success": True,
            "draft_id": row["id"],
            "template_name": row["template_name"],
            "status": row["status"],
            "data": json.loads(row["data"]),
            "output_filename": row["output_filename"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
    finally:
        conn.close()


def list_drafts(status: str | None = None) -> dict[str, Any]:
    conn = _get_conn()
    try:
        if status:
            rows = conn.execute("SELECT * FROM drafts WHERE status = ? ORDER BY updated_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM drafts ORDER BY updated_at DESC").fetchall()
        drafts = []
        for row in rows:
            drafts.append({
                "draft_id": row["id"],
                "template_name": row["template_name"],
                "status": row["status"],
                "data": json.loads(row["data"]),
                "output_filename": row["output_filename"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            })
        return {"success": True, "drafts": drafts, "total": len(drafts)}
    finally:
        conn.close()


def delete_draft(draft_id: str) -> dict[str, Any]:
    conn = _get_conn()
    try:
        conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
        conn.commit()
        return {"success": True, "draft_id": draft_id}
    finally:
        conn.close()


def set_draft_status(draft_id: str, status: str, output_filename: str | None = None) -> dict[str, Any]:
    conn = _get_conn()
    try:
        now = datetime.now(timezone.utc).isoformat()
        if output_filename:
            conn.execute(
                "UPDATE drafts SET status = ?, output_filename = ?, updated_at = ? WHERE id = ?",
                (status, output_filename, now, draft_id),
            )
        else:
            conn.execute(
                "UPDATE drafts SET status = ?, updated_at = ? WHERE id = ?",
                (status, now, draft_id),
            )
        conn.commit()
        return {"success": True, "draft_id": draft_id, "status": status}
    finally:
        conn.close()
