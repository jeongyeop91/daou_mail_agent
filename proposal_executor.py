from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from core.proposals import list_proposals, update_proposal_status

EXEC_PATH = Path(__file__).resolve().parent / 'data' / 'proposal_executions.json'


def _load_execs() -> list[dict]:
    if not EXEC_PATH.exists():
        return []
    try:
        return json.loads(EXEC_PATH.read_text())
    except Exception:
        return []


def _save_execs(items: list[dict]) -> None:
    EXEC_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXEC_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2))


def execute_approved_proposal(proposal_id: int) -> str:
    proposal = next((item for item in list_proposals() if item.get('id') == proposal_id), None)
    if not proposal:
        return '해당 제안을 찾지 못했습니다.'
    if proposal.get('status') != 'approved':
        return '먼저 해당 제안을 승인해 주세요.'
    executions = _load_execs()
    executions.append({
        'proposal_id': proposal_id,
        'title': proposal.get('title'),
        'executed_at': datetime.now().isoformat(timespec='seconds'),
        'result': 'executed',
    })
    _save_execs(executions)
    update_proposal_status(proposal_id, 'executed')
    return f"제안 #{proposal_id} 실행을 기록했습니다."
