from __future__ import annotations

import email
import imaplib
from email.header import decode_header, make_header
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


def fetch_unread_emails(limit: int = 10) -> list[EmailItem]:
    settings = load_settings()
    if not settings.imap_host or not settings.email_address or not settings.email_password:
        return []
    mail = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    mail.login(settings.email_address, settings.email_password)
    mail.select('INBOX')
    status, data = mail.search(None, 'UNSEEN')
    ids = data[0].split()[-limit:]
    items: list[EmailItem] = []
    for msg_id in reversed(ids):
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        if status != 'OK':
            continue
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        body, has_attachments = _extract_body(msg)
        items.append(EmailItem(
            sender=_decode(msg.get('From')),
            subject=_decode(msg.get('Subject')),
            date=_decode(msg.get('Date')),
            body=body,
            has_attachments=has_attachments,
        ))
    mail.logout()
    return items


def filter_emails_by_keyword(emails: Iterable[EmailItem], keyword: str) -> list[EmailItem]:
    keyword = (keyword or '').strip().lower()
    if not keyword:
        return list(emails)
    return [e for e in emails if keyword in f'{e.subject} {e.sender} {e.body}'.lower()]
