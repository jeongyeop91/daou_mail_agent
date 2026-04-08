from __future__ import annotations

from agents.advisor import suggest_next_action
from agents.classifier import classify_email
from briefings.mail_action_builder import build_mail_action_keyboard
from category_rules import categorize_email
from storage.mail_cache import get_cached_reply_needed_emails, mark_briefed


def build_reply_needed_briefing(limit: int = 10) -> tuple[str, list, dict | None]:
    filtered = get_cached_reply_needed_emails(limit, unbriefed_only=True)
    if not filtered:
        return '현재 새롭게 브리핑할 답장 필요 메일은 없습니다.', [], None
    lines = [
        '📮 답장 필요한 메일 브리핑',
        '━━━━━━━━━━',
        '현재 상태',
        f'- 새 답장 필요 메일: {len(filtered)}건',
        '- 회신 또는 확인이 필요한 메일만 정리했습니다.',
        '',
        '상세 목록',
    ]
    selected = filtered[:5]
    for idx, email in enumerate(selected, start=1):
        lines.append(f'{idx}. [{classify_email(email)}/{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append(f'권장 조치: {suggest_next_action(email)}')
        lines.append('바로 하기는 아래 버튼에서 실행할 수 있습니다.')
        lines.append('')
    return '\n'.join(lines[:-1]), selected, build_mail_action_keyboard(selected, primary='draft')


def mark_reply_briefed(emails: list) -> int:
    return mark_briefed(emails)
