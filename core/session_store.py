from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from core.models import EmailItem

DATA_PATH = Path(__file__).resolve().parent.parent / 'data' / 'last_results.json'


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
