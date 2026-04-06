from __future__ import annotations

from agents.classifier import classify_email
from category_rules import categorize_email
from core.models import EmailItem


def suggest_next_action(email: EmailItem) -> str:
    category = categorize_email(email)
    text = f'{email.subject} {email.body}'
    if category == '결재':
        return '결재 관련 메일이므로 우선 확인하신 뒤 승인 또는 검토가 필요한지 판단하시는 것이 좋겠습니다.'
    if category == '보안':
        return '보안 관련 안내이므로 필수 조치나 기한이 있는지 먼저 확인하시는 것을 권장드립니다.'
    if any(token in text for token in ['회신', '확인', '검토', '승인']):
        return '답장 또는 확인이 필요한 내용으로 보여, 상세 내용을 검토하신 뒤 회신 초안을 준비하시는 것이 적절해 보입니다.'
    if classify_email(email) == '중요':
        return '중요 메일로 분류되므로 우선순위를 높게 두고 먼저 확인하시는 것을 권장드립니다.'
    return '긴급도는 높아 보이지 않지만 내용을 확인하신 뒤 필요 시 분류 또는 보관하시면 됩니다.'
