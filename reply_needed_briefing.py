from __future__ import annotations

from agents.advisor import suggest_next_action
from agents.classifier import classify_email
from briefing_actions import BriefingAction, build_inline_keyboard
from category_rules import categorize_email
from mail_cache import get_cached_reply_needed_emails, mark_briefed


def build_reply_needed_briefing(limit: int = 10) -> tuple[str, list, dict | None]:
    filtered = get_cached_reply_needed_emails(limit, unbriefed_only=True)
    if not filtered:
        return '새롭게 브리핑할 답장 필요 메일이 없습니다.', [], None
    lines = ['📮 답장 필요한 메일 브리핑', '━━━━━━━━━━', f'답장 필요 = {len(filtered)}건', '']
    selected = filtered[:5]
    actions: list[BriefingAction] = []
    for idx, email in enumerate(selected, start=1):
        lines.append(f'{idx}. [{classify_email(email)}/{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
        actions.append(BriefingAction(f'✍️ {idx}번 답장 초안', f'{idx}번 메일 답장 초안 써줘'))
        lines.append(f'권장 조치: {suggest_next_action(email)}')
        lines.append(f'바로 하기: {idx}번 메일 답장 초안 써줘')
        lines.append('')
    return '\n'.join(lines[:-1]), selected, build_inline_keyboard(actions, row_size=1)


def mark_reply_briefed(emails: list) -> int:
    return mark_briefed(emails)
