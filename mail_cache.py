from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from core.models import EmailItem

DB_PATH = Path(__file__).resolve().parent / 'data' / 'mail_cache.db'


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_mail_cache() -> None:
    with _connect() as conn:
        conn.executescript(
            '''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_key TEXT NOT NULL UNIQUE,
                mailbox TEXT NOT NULL DEFAULT 'INBOX',
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                raw_date TEXT NOT NULL,
                received_at TEXT,
                body_preview TEXT NOT NULL,
                has_attachments INTEGER NOT NULL DEFAULT 0,
                classification TEXT,
                needs_reply INTEGER NOT NULL DEFAULT 0,
                is_important INTEGER NOT NULL DEFAULT 0,
                source_kind TEXT NOT NULL DEFAULT 'unknown',
                first_seen_at TEXT NOT NULL,
                last_seen_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_messages_received_at ON messages(received_at DESC);
            CREATE INDEX IF NOT EXISTS idx_messages_last_seen_at ON messages(last_seen_at DESC);
            CREATE INDEX IF NOT EXISTS idx_messages_source_kind ON messages(source_kind);

            CREATE TABLE IF NOT EXISTS sync_state (
                mailbox TEXT PRIMARY KEY,
                last_sync_at TEXT,
                last_source_kind TEXT
            );
            '''
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_iso(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def _message_key(email: EmailItem) -> str:
    base = '\n'.join([
        email.sender.strip(),
        email.subject.strip(),
        email.date.strip(),
        (email.body or '')[:1000].strip(),
    ])
    return hashlib.sha256(base.encode('utf-8', errors='ignore')).hexdigest()


def cache_emails(emails: list[EmailItem], *, source_kind: str, mailbox: str = 'INBOX') -> int:
    if not emails:
        return 0
    init_mail_cache()
    now = _now_iso()
    inserted_or_updated = 0
    with _connect() as conn:
        for email in emails:
            preview = (email.body or '').strip().replace('\x00', '')[:500]
            conn.execute(
                '''
                INSERT INTO messages (
                    message_key, mailbox, sender, subject, raw_date, received_at,
                    body_preview, has_attachments, source_kind, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_key) DO UPDATE SET
                    sender=excluded.sender,
                    subject=excluded.subject,
                    raw_date=excluded.raw_date,
                    received_at=excluded.received_at,
                    body_preview=excluded.body_preview,
                    has_attachments=excluded.has_attachments,
                    source_kind=excluded.source_kind,
                    last_seen_at=excluded.last_seen_at
                ''',
                (
                    _message_key(email),
                    mailbox,
                    email.sender,
                    email.subject,
                    email.date,
                    _safe_iso(email.parsed_date),
                    preview,
                    1 if email.has_attachments else 0,
                    source_kind,
                    now,
                    now,
                ),
            )
            inserted_or_updated += 1
        conn.execute(
            '''
            INSERT INTO sync_state(mailbox, last_sync_at, last_source_kind)
            VALUES (?, ?, ?)
            ON CONFLICT(mailbox) DO UPDATE SET
                last_sync_at=excluded.last_sync_at,
                last_source_kind=excluded.last_source_kind
            ''',
            (mailbox, now, source_kind),
        )
    return inserted_or_updated


def get_cached_recent(limit: int = 10) -> list[sqlite3.Row]:
    init_mail_cache()
    with _connect() as conn:
        return conn.execute(
            '''
            SELECT sender, subject, raw_date, received_at, body_preview, has_attachments, source_kind, last_seen_at
            FROM messages
            ORDER BY COALESCE(received_at, last_seen_at) DESC, id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
