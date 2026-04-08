from __future__ import annotations

import json
import hashlib
from dataclasses import asdict
from pathlib import Path

from core.models import EmailItem

DATA_PATH = Path(__file__).resolve().parent.parent / 'data' / 'last_results.json'
BUTTON_PATH = Path(__file__).resolve().parent.parent / 'data' / 'button_targets.json'


def save_last_results(command: str, emails: list[EmailItem]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps({'command': command, 'emails': [asdict(e) for e in emails]}, ensure_ascii=False, indent=2, default=str))


def load_last_results() -> dict:
    if not DATA_PATH.exists():
        return {}
    try:
        return json.loads(DATA_PATH.read_text())
    except Exception:
        return {}


def get_email_by_index(index: int):
    data = load_last_results()
    emails = data.get('emails', [])
    if 1 <= index <= len(emails):
        return emails[index - 1]
    return None


def _email_token(email: EmailItem) -> str:
    base = '|'.join([email.sender, email.subject, email.date])
    return hashlib.sha1(base.encode('utf-8', errors='ignore')).hexdigest()[:16]


def _load_button_targets() -> dict:
    if not BUTTON_PATH.exists():
        return {}
    try:
        return json.loads(BUTTON_PATH.read_text())
    except Exception:
        return {}


def _save_button_targets(items: dict) -> None:
    BUTTON_PATH.parent.mkdir(parents=True, exist_ok=True)
    BUTTON_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2, default=str))


def save_button_target(email: EmailItem) -> str:
    token = _email_token(email)
    items = _load_button_targets()
    items[token] = asdict(email)
    _save_button_targets(items)
    return token


def get_email_by_token(token: str):
    items = _load_button_targets()
    return items.get(token)
