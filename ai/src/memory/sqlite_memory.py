import sqlite3
import uuid
from datetime import datetime
from typing import Optional


def init_db(db_path: str = "chat_sessions.db") -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TEXT
        )
        """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    return conn


def get_or_create_user(conn: sqlite3.Connection, user_id: str) -> str:
    """Garante que o usuário existe no banco. Cria se não existir."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    if cur.fetchone() is None:
        created_at = datetime.utcnow().isoformat()
        conn.execute(
            "INSERT INTO users (id, created_at) VALUES (?, ?)",
            (user_id, created_at),
        )
        conn.commit()
    return user_id


def create_session(conn: sqlite3.Connection, user_id: str) -> str:
    session_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO sessions (id, user_id, created_at) VALUES (?, ?, ?)",
        (session_id, user_id, created_at),
    )
    conn.commit()
    return session_id


def persist_message(conn: sqlite3.Connection, session_id: str, role: str, content: str) -> None:
    created_at = datetime.utcnow().isoformat()
    conn.execute(
        "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
        (session_id, role, content, created_at),
    )
    conn.commit()


def get_conversation_history(conn: sqlite3.Connection, user_id: str, limit: int = 20):
    """Retorna o histórico de conversas reais (usuário e assistente) em ordem cronológica."""
    cur = conn.cursor()
    cur.execute(
        """SELECT m.role, m.content, m.created_at
           FROM messages m
           JOIN sessions s ON m.session_id = s.id
           WHERE s.user_id = ? AND m.role IN ('user', 'assistant')
           ORDER BY m.id DESC LIMIT ?""",
        (user_id, limit),
    )
    rows = cur.fetchall()
    return [
        {"role": r[0], "content": r[1], "created_at": r[2]} for r in reversed(rows)
    ]


def get_recent_messages(conn: sqlite3.Connection, user_id: str, limit: int = 20, include_internal: bool = False):
    """Retorna mensagens recentes do usuário em ordem cronológica."""
    if not include_internal:
        return get_conversation_history(conn, user_id, limit)

    cur = conn.cursor()
    cur.execute(
        """SELECT m.role, m.content, m.created_at
           FROM messages m
           JOIN sessions s ON m.session_id = s.id
           WHERE s.user_id = ?
           ORDER BY m.id DESC LIMIT ?""",
        (user_id, limit),
    )
    rows = cur.fetchall()
    return [
        {"role": r[0], "content": r[1], "created_at": r[2]} for r in reversed(rows)
    ]


def build_memory_context(conn: sqlite3.Connection, user_id: str, limit: int = 20) -> str:
    """Constrói um bloco contextual legível com as mensagens anteriores do usuário e do assistente.

    Filtra ruídos técnicos internos (como JSON bruto do especialista ou saídas do juiz)
    para fornecer apenas o diálogo real entre usuário e assistente.
    """
    msgs = get_conversation_history(conn, user_id, limit)
    if not msgs:
        return ""
    parts = []
    for m in msgs:
        role_label = "Usuário" if m["role"] == "user" else "Assistente"
        content = m["content"].strip()
        parts.append(f"[{role_label}]: {content}")
    return "\n\n".join(parts)
