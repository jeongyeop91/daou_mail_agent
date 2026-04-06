from __future__ import annotations

from category_rules import categorize_email
from core.models import EmailItem


def classify_email(email: EmailItem) -> str:
    category = categorize_email(email)
    if category in {'결재', '보안'}:
        return '중요'
    text = f'{email.subject} {email.body}'.lower()
    if any(token in text for token in ['긴급', 'urgent', '즉시', '마감']):
        return '중요'
    return '일반'
