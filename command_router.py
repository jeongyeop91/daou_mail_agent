from __future__ import annotations

from agents.classifier import classify_email
from agents.collector import fetch_recent_emails, fetch_unread_emails, filter_emails_by_keyword
from agents.drafter import draft_reply
from core.models import EmailItem
from core.session_store import get_email_by_index, save_last_results
from intent_parser import Intent


def _filter_important(emails: list[EmailItem], important_only: bool) -> list[EmailItem]:
    if not important_only:
        return emails
    return [email for email in emails if classify_email(email) == '중요']


def _load_reference_email(index: int | None) -> EmailItem | None:
    if not index:
        return None
    saved = get_email_by_index(index)
    if saved:
        return EmailItem(**saved)

    fallback_emails = fetch_recent_emails(limit=max(index, 10))
    if len(fallback_emails) >= index:
        save_last_results('자동 복구: 최근 메일 목록', fallback_emails)
        return fallback_emails[index - 1]
    return None


def run_command(intent: Intent):
    if intent.action in {'detail', 'draft'} and intent.reference_index:
        email = _load_reference_email(intent.reference_index)
        if not email:
            return '참조할 메일을 찾지 못했습니다. 먼저 메일 목록을 조회해 주세요.'
        if intent.action == 'draft':
            return draft_reply(email)
        return [email]

    fetch_limit = max(intent.limit, 20) if intent.important_only or intent.keyword else intent.limit
    if intent.action in {'list', 'detail'} and not intent.important_only and not intent.keyword:
        emails = fetch_recent_emails(limit=fetch_limit)
    else:
        emails = fetch_unread_emails(limit=fetch_limit)
    emails = filter_emails_by_keyword(emails, intent.keyword)
    emails = _filter_important(emails, intent.important_only)
    emails = emails[:intent.limit]

    if intent.action == 'draft':
        if not emails:
            return '답장 초안을 만들 메일이 없습니다.'
        return draft_reply(emails[0])
    return emails
