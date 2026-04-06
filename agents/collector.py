from __future__ import annotations

import email
import imaplib
from datetime import datetime, timezone
from email.header import decode_header, make_header
from email.utils import parsedate_to_datetime
from typing import Iterable

from core.config import load_settings
from core.models import EmailItem


def _decode(value: str | bytes | None) -> str:
    if not value:
        return ''
    try:
        return str(make_header(decode_header(value)))
    except Exception:
        return str(value)


def _extract_body(msg) -> tuple[str, bool]:
    has_attachments = False
    if msg.is_multipart():
        parts: list[str] = []
        for part in msg.walk():
            disposition = str(part.get('Content-Disposition') or '')
            if 'attachment' in disposition.lower():
                has_attachments = True
            ctype = part.get_content_type()
            if ctype == 'text/plain' and 'attachment' not in disposition.lower():
                payload = part.get_payload(decode=True) or b''
                charset = part.get_content_charset() or 'utf-8'
                try:
                    parts.append(payload.decode(charset, errors='ignore'))
                except Exception:
                    parts.append(payload.decode('utf-8', errors='ignore'))
        return '\n'.join(parts).strip(), has_attachments
    payload = msg.get_payload(decode=True) or b''
    charset = msg.get_content_charset() or 'utf-8'
    try:
        body = payload.decode(charset, errors='ignore')
    except Exception:
        body = payload.decode('utf-8', errors='ignore')
    return body.strip(), has_attachments


def _extract_rfc822_bytes(msg_data) -> bytes | None:
    if not msg_data:
        return None
    for part in msg_data:
        if isinstance(part, tuple) and len(part) >= 2 and isinstance(part[1], (bytes, bytearray)):
            return bytes(part[1])
    return None


def _parse_email_date(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


def _fetch_emails(search_criterion: str = 'UNSEEN', limit: int = 10) -> list[EmailItem]:
    settings = load_settings()
    if not settings.imap_host or not settings.email_address or not settings.email_password:
        return []

    mail = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    try:
        mail.login(settings.email_address, settings.email_password)
        select_status, select_data = mail.select('INBOX')
        if select_status != 'OK':
            return []

        ids: list[bytes] = []
        if search_criterion == 'RECENT_SEQUENCE':
            total = int(select_data[0]) if select_data and select_data[0] else 0
            start = max(total - max(limit * 3, limit) + 1, 1)
            ids = [str(i).encode() for i in range(start, total + 1)]
        else:
            status, data = mail.search(None, search_criterion)
            if status != 'OK' or not data or not data[0]:
                return []
            ids = data[0].split()[-max(limit * 3, limit):]

        items: list[EmailItem] = []
        for msg_id in reversed(ids):
            try:
                status, msg_data = mail.fetch(msg_id, '(BODY.PEEK[])')
                if status != 'OK':
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue

                raw = _extract_rfc822_bytes(msg_data)
                if not raw:
                    continue

                msg = email.message_from_bytes(raw)
                body, has_attachments = _extract_body(msg)
                items.append(EmailItem(
                    sender=_decode(msg.get('From')),
                    subject=_decode(msg.get('Subject')),
                    date=_decode(msg.get('Date')),
                    body=body,
                    has_attachments=has_attachments,
                ))
            except imaplib.IMAP4.abort:
                continue
            except Exception:
                continue

        items.sort(key=lambda item: _parse_email_date(item.date), reverse=True)
        return items[:limit]
    finally:
        try:
            mail.logout()
        except Exception:
            pass


def fetch_unread_emails(limit: int = 10) -> list[EmailItem]:
    return _fetch_emails('UNSEEN', limit)


def fetch_recent_emails(limit: int = 10) -> list[EmailItem]:
    return _fetch_emails('RECENT_SEQUENCE', limit)


def filter_emails_by_keyword(emails: Iterable[EmailItem], keyword: str) -> list[EmailItem]:
    keyword = (keyword or '').strip().lower()
    if not keyword:
        return list(emails)
    return [e for e in emails if keyword in f'{e.subject} {e.sender} {e.body}'.lower()]
