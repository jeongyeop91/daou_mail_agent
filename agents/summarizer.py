from __future__ import annotations

from core.models import EmailItem


def summarize_email(email: EmailItem, max_len: int = 120) -> str:
    text = ' '.join(email.body.split())
    if not text:
        return '본문이 없습니다.'
    return text[:max_len] + ('...' if len(text) > max_len else '')
