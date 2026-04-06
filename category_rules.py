from __future__ import annotations

from core.models import EmailItem


def categorize_email(email: EmailItem) -> str:
    text = f'{email.subject} {email.body}'.lower()
    if '결재' in text or '승인' in text:
        return '결재'
    if '보안' in text or '만료' in text or '인증' in text:
        return '보안'
    if '공지' in text or '안내' in text:
        return '공지'
    if '광고' in text or 'promotion' in text:
        return '광고'
    if '회의' in text or '견적' in text or '요청' in text or '검토' in text:
        return '업무'
    return '기타'
