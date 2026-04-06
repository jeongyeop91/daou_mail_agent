from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from core.proposals import list_proposals, update_proposal_status

EXEC_PATH = Path(__file__).resolve().parent.parent / 'data' / 'proposal_executions.json'


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


def _run_calendar_cmd(cmd: list[str], failure_prefix: str) -> str | None:
    import subprocess
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return None
    except subprocess.CalledProcessError as e:
        message = (e.stderr or e.stdout or '').strip()
        return f'{failure_prefix}: {message or e.returncode}'


def _execute_calendar_register(payload: dict) -> str:
    cmd = [
        'gog', 'calendar', 'create', 'primary',
        '--summary', payload['title'],
        '--from', payload['start_at'],
        '--to', payload['end_at'],
    ]
    if payload.get('description'):
        cmd.extend(['--description', payload['description']])
    if payload.get('location'):
        cmd.extend(['--location', payload['location']])
    error = _run_calendar_cmd(cmd, '구글 일정 등록에 실패했습니다')
    if error:
        return error
    return f"구글 일정 등록을 완료했습니다: {payload['title']}"


def _execute_calendar_update(payload: dict) -> str:
    cmd = [
        'gog', 'calendar', 'update', 'primary', payload['event_id'],
        '--summary', payload['title'],
        '--from', payload['start_at'],
        '--to', payload['end_at'],
    ]
    if payload.get('description'):
        cmd.extend(['--description', payload['description']])
    if payload.get('location'):
        cmd.extend(['--location', payload['location']])
    error = _run_calendar_cmd(cmd, '구글 일정 수정에 실패했습니다')
    if error:
        return error
    return f"구글 일정 수정을 완료했습니다: {payload['title']}"


def _execute_calendar_cancel(payload: dict) -> str:
    cmd = ['gog', 'calendar', 'delete', 'primary', payload['event_id']]
    error = _run_calendar_cmd(cmd, '구글 일정 취소에 실패했습니다')
    if error:
        return error
    return f"구글 일정 취소를 완료했습니다: {payload['title']}"


def execute_approved_proposal(proposal_id: int) -> str:
    proposal = next((item for item in list_proposals() if item.get('id') == proposal_id), None)
    if not proposal:
        return '해당 제안을 찾지 못했습니다.'
    if proposal.get('status') != 'approved':
        return '먼저 해당 제안을 승인해 주세요.'
    payload = proposal.get('payload') or {}
    result_text = 'executed'
    if payload.get('kind') == 'calendar_register':
        result_text = _execute_calendar_register(payload)
        if result_text.startswith('구글 일정 등록에 실패했습니다'):
            return result_text
    elif payload.get('kind') == 'calendar_update':
        result_text = _execute_calendar_update(payload)
        if result_text.startswith('구글 일정 수정에 실패했습니다'):
            return result_text
    elif payload.get('kind') == 'calendar_cancel':
        result_text = _execute_calendar_cancel(payload)
        if result_text.startswith('구글 일정 취소에 실패했습니다'):
            return result_text
    executions = _load_execs()
    executions.append({
        'proposal_id': proposal_id,
        'title': proposal.get('title'),
        'executed_at': datetime.now().isoformat(timespec='seconds'),
        'result': result_text,
    })
    _save_execs(executions)
    update_proposal_status(proposal_id, 'executed')
    return f"제안 #{proposal_id} 실행을 기록했습니다.\n{result_text}"
