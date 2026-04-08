from __future__ import annotations

from agents.advisor import suggest_next_action
from agents.classifier import classify_email
from briefings.mail_action_builder import build_mail_action_keyboard
from category_rules import categorize_email
from storage.mail_cache import get_cached_important_emails, mark_notified


def build_important_mail_briefing(limit: int = 5, *, unnotified_only: bool = True) -> tuple[str, list, dict | None]:
    emails = get_cached_important_emails(limit, unnotified_only=unnotified_only)
    if not emails:
        return '현재 새롭게 알릴 중요 메일은 없습니다.', [], None

    lines = [
        '📮 중요 메일 알림',
        '━━━━━━━━━━',
        '현재 상태',
        f'- 새 중요 메일: {len(emails)}건',
        '- 우선 확인이 필요한 메일만 추렸습니다.',
        '',
        '상세 목록',
    ]
    for idx, email in enumerate(emails, start=1):
        lines.append(f'{idx}. [{classify_email(email)}/{categorize_email(email)}] {email.subject}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append(f'권장 조치: {suggest_next_action(email)}')
        lines.append('바로 하기는 아래 버튼에서 실행할 수 있습니다.')
        lines.append('')
    return '\n'.join(lines[:-1]), emails, build_mail_action_keyboard(emails, primary='detail')


def mark_important_notified(emails: list) -> int:
    return mark_notified(emails)
