from __future__ import annotations

from agents.advisor import suggest_next_action
from agents.classifier import classify_email
from category_rules import categorize_email
from mail_cache import get_cached_important_emails, mark_notified


def build_important_mail_briefing(limit: int = 5, *, unnotified_only: bool = True) -> tuple[str, list]:
    emails = get_cached_important_emails(limit, unnotified_only=unnotified_only)
    if not emails:
        return '새롭게 알릴 중요 메일이 없습니다.', []

    lines = ['📮 중요 메일 알림', '━━━━━━━━━━', f'중요 메일 = {len(emails)}건', '']
    for idx, email in enumerate(emails, start=1):
        lines.append(f'{idx}. [{classify_email(email)}/{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append(f'권장 조치: {suggest_next_action(email)}')
        lines.append('')
    return '\n'.join(lines[:-1]), emails


def build_and_mark_important_mail_briefing(limit: int = 5) -> str:
    text, emails = build_important_mail_briefing(limit, unnotified_only=True)
    if emails:
        mark_notified(emails)
    return text
