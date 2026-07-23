import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

VALID_STATUSES = {"draft", "completed"}

DB_DIR = Path(os.getenv("OUTPUT_DIR", str(Path(__file__).parent.parent / "output")))
DB_PATH = DB_DIR / "drafts.db"


def _row_to_draft(row: sqlite3.Row) -> dict[str, Any]:
    try:
        data = json.loads(row["data"])
    except json.JSONDecodeError:
        data = {}
    return {
        "draft_id": row["id"],
        "template_name": row["template_name"],
        "status": row["status"],
        "data": data,
        "output_filename": row["output_filename"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _ok(**kwargs: Any) -> dict[str, Any]:
    return {"success": True, **kwargs}


def _err(message: str) -> dict[str, Any]:
    return {"success": False, "error": message}


@contextmanager
def _get_conn():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
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
    try:
        yield conn
    finally:
        conn.close()


def create_draft(template_name: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    with _get_conn() as conn:
        draft_id = uuid.uuid4().hex[:12]
        conn.execute(
            "INSERT INTO drafts (id, template_name, status, data, created_at, updated_at) VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))",
            (draft_id, template_name, "draft", json.dumps(data or {})),
        )
        conn.commit()
        return _ok(draft_id=draft_id)


def update_draft(draft_id: str, data: dict[str, Any]) -> dict[str, Any]:
    with _get_conn() as conn:
        row = conn.execute("SELECT data FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if row is None:
            return _err(f"Draft '{draft_id}' not found")
        try:
            current = json.loads(row["data"])
        except json.JSONDecodeError:
            current = {}
        merged = {**current, **data}
        conn.execute("UPDATE drafts SET data = ?, updated_at = datetime('now') WHERE id = ?", (json.dumps(merged), draft_id))
        conn.commit()
        return _ok(draft_id=draft_id, data=merged)


def get_draft(draft_id: str) -> dict[str, Any]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM drafts WHERE id = ?", (draft_id,)).fetchone()
        if row is None:
            return _err(f"Draft '{draft_id}' not found")
        return _ok(**_row_to_draft(row))


def list_drafts(status: str | None = None) -> dict[str, Any]:
    with _get_conn() as conn:
        if status:
            rows = conn.execute("SELECT * FROM drafts WHERE status = ? ORDER BY updated_at DESC", (status,)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM drafts ORDER BY updated_at DESC").fetchall()
        drafts = [_row_to_draft(row) for row in rows]
        return _ok(drafts=drafts, total=len(drafts))


def delete_draft(draft_id: str) -> dict[str, Any]:
    with _get_conn() as conn:
        cursor = conn.execute("DELETE FROM drafts WHERE id = ?", (draft_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return _err(f"Draft '{draft_id}' not found")
        return _ok(draft_id=draft_id)


def set_draft_status(draft_id: str, status: str, output_filename: str | None = None) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        return _err(f"Invalid status '{status}'. Must be one of: {', '.join(sorted(VALID_STATUSES))}")
    with _get_conn() as conn:
        if output_filename:
            cursor = conn.execute(
                "UPDATE drafts SET status = ?, output_filename = ?, updated_at = datetime('now') WHERE id = ?",
                (status, output_filename, draft_id),
            )
        else:
            cursor = conn.execute(
                "UPDATE drafts SET status = ?, updated_at = datetime('now') WHERE id = ?",
                (status, draft_id),
            )
        conn.commit()
        if cursor.rowcount == 0:
            return _err(f"Draft '{draft_id}' not found")
        return _ok(draft_id=draft_id, status=status)
