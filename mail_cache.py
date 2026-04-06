from __future__ import annotations

import hashlib
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from agents.classifier import classify_email
from category_rules import categorize_email
from core.models import EmailItem

REPLY_HINTS = ('회신', '확인', '검토', '승인')

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
                notified_at TEXT,
                briefed_at TEXT,
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
        existing_columns = {row['name'] for row in conn.execute('PRAGMA table_info(messages)').fetchall()}
        if 'notified_at' not in existing_columns:
            conn.execute('ALTER TABLE messages ADD COLUMN notified_at TEXT')
        if 'briefed_at' not in existing_columns:
            conn.execute('ALTER TABLE messages ADD COLUMN briefed_at TEXT')


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


def _needs_reply(email: EmailItem) -> bool:
    text = f'{email.subject} {email.body}'
    return any(token in text for token in REPLY_HINTS)


def cache_emails(emails: list[EmailItem], *, source_kind: str, mailbox: str = 'INBOX') -> int:
    if not emails:
        return 0
    init_mail_cache()
    now = _now_iso()
    inserted_or_updated = 0
    with _connect() as conn:
        for email in emails:
            preview = (email.body or '').strip().replace('\x00', '')[:500]
            category = categorize_email(email)
            importance = classify_email(email)
            needs_reply = _needs_reply(email)
            conn.execute(
                '''
                INSERT INTO messages (
                    message_key, mailbox, sender, subject, raw_date, received_at,
                    body_preview, has_attachments, classification, needs_reply, is_important, source_kind, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(message_key) DO UPDATE SET
                    sender=excluded.sender,
                    subject=excluded.subject,
                    raw_date=excluded.raw_date,
                    received_at=excluded.received_at,
                    body_preview=excluded.body_preview,
                    has_attachments=excluded.has_attachments,
                    classification=excluded.classification,
                    needs_reply=excluded.needs_reply,
                    is_important=excluded.is_important,
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
                    category,
                    1 if needs_reply else 0,
                    1 if importance == '중요' else 0,
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


def _row_to_email(row: sqlite3.Row) -> EmailItem:
    parsed_date = None
    received_at = row['received_at']
    if received_at:
        try:
            parsed_date = datetime.fromisoformat(received_at)
        except Exception:
            parsed_date = None
    return EmailItem(
        sender=row['sender'],
        subject=row['subject'],
        date=row['raw_date'],
        body=row['body_preview'] or '',
        has_attachments=bool(row['has_attachments']),
        parsed_date=parsed_date,
    )


def get_cached_recent(limit: int = 10) -> list[sqlite3.Row]:
    init_mail_cache()
    with _connect() as conn:
        return conn.execute(
            '''
            SELECT sender, subject, raw_date, received_at, body_preview, has_attachments, classification, needs_reply, is_important, source_kind, last_seen_at
            FROM messages
            ORDER BY COALESCE(received_at, last_seen_at) DESC, id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()


def get_cached_recent_emails(limit: int = 10) -> list[EmailItem]:
    return [_row_to_email(row) for row in get_cached_recent(limit)]


def get_cached_reply_needed_emails(limit: int = 10, *, unbriefed_only: bool = False) -> list[EmailItem]:
    init_mail_cache()
    with _connect() as conn:
        rows = conn.execute(
            f'''
            SELECT sender, subject, raw_date, received_at, body_preview, has_attachments, classification, needs_reply, is_important, source_kind, last_seen_at
            FROM messages
            WHERE needs_reply = 1 {'AND briefed_at IS NULL' if unbriefed_only else ''}
            ORDER BY COALESCE(received_at, last_seen_at) DESC, id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    return [_row_to_email(row) for row in rows]


def _mark_timestamp(emails: list[EmailItem], column: str) -> int:
    if not emails:
        return 0
    init_mail_cache()
    now = _now_iso()
    updated = 0
    with _connect() as conn:
        for email in emails:
            result = conn.execute(
                f'''UPDATE messages
                SET {column} = ?
                WHERE sender = ? AND subject = ? AND raw_date = ?''',
                (now, email.sender, email.subject, email.date),
            )
            updated += result.rowcount
    return updated


def mark_briefed(emails: list[EmailItem]) -> int:
    return _mark_timestamp(emails, 'briefed_at')


def mark_notified(emails: list[EmailItem]) -> int:
    return _mark_timestamp(emails, 'notified_at')


def get_cached_important_emails(limit: int = 10, *, unnotified_only: bool = False) -> list[EmailItem]:
    init_mail_cache()
    with _connect() as conn:
        rows = conn.execute(
            f'''
            SELECT sender, subject, raw_date, received_at, body_preview, has_attachments, classification, needs_reply, is_important, source_kind, last_seen_at
            FROM messages
            WHERE is_important = 1 {'AND notified_at IS NULL' if unnotified_only else ''}
            ORDER BY COALESCE(received_at, last_seen_at) DESC, id DESC
            LIMIT ?
            ''',
            (limit,),
        ).fetchall()
    return [_row_to_email(row) for row in rows]
