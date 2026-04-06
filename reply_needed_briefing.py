from __future__ import annotations

from agents.advisor import suggest_next_action
from agents.classifier import classify_email
from category_rules import categorize_email
from command_router import run_command
from intent_parser import Intent

REPLY_HINTS = ['회신', '확인', '검토', '승인']


def build_reply_needed_briefing(limit: int = 10) -> str:
    result = run_command(Intent(action='summary', limit=limit))
    if isinstance(result, str):
        return result
    filtered = [email for email in result if any(h in f'{email.subject} {email.body}' for h in REPLY_HINTS)]
    if not filtered:
        return '답장이나 확인이 필요한 메일이 없습니다.'
    lines = ['📮 답장 필요한 메일 브리핑', '━━━━━━━━━━', f'답장 필요 = {len(filtered)}건', '']
    for idx, email in enumerate(filtered[:5], start=1):
        lines.append(f'{idx}. [{classify_email(email)}/{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append(f'권장 조치: {suggest_next_action(email)}')
        lines.append(f'바로 하기: {idx}번 메일 답장 초안 써줘')
        lines.append('')
    return '\n'.join(lines[:-1])
