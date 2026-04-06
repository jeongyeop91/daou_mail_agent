from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / 'data' / 'pending_proposals.json'


def _load() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    try:
        return json.loads(DATA_PATH.read_text())
    except Exception:
        return []


def _save(items: list[dict]) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2))


def create_proposal(title: str, payload: dict) -> dict:
    items = _load()
    next_id = (max((item.get('id', 0) for item in items), default=0) + 1)
    proposal = {
        'id': next_id,
        'title': title,
        'payload': payload,
        'status': 'pending',
        'created_at': datetime.now().isoformat(timespec='seconds'),
    }
    items.append(proposal)
    _save(items)
    return proposal


def list_proposals(status: str | None = None) -> list[dict]:
    items = _load()
    if status:
        return [item for item in items if item.get('status') == status]
    return items


def update_proposal_status(proposal_id: int, status: str) -> dict | None:
    items = _load()
    target = None
    for item in items:
        if item.get('id') == proposal_id:
            item['status'] = status
            item['updated_at'] = datetime.now().isoformat(timespec='seconds')
            target = item
            break
    _save(items)
    return target
