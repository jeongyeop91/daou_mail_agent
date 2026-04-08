from __future__ import annotations

from briefing_actions import BriefingAction, build_inline_keyboard
from core.models import EmailItem
from core.session_store import save_button_target
from schedule_mail import extract_schedule_candidate


def build_mail_action_keyboard(emails: list[EmailItem], *, primary: str = 'detail') -> dict | None:
    actions: list[BriefingAction] = []
    for idx, email in enumerate(emails, start=1):
        token = save_button_target(email)
        if primary == 'detail':
            actions.append(BriefingAction(f'📄 {idx}번 메일 보기', f'@mailtoken:{token}:detail'))
        elif primary == 'draft':
            actions.append(BriefingAction(f'✍️ {idx}번 답장 초안', f'@mailtoken:{token}:draft'))
        elif primary == 'schedule':
            candidate = extract_schedule_candidate(email)
            if candidate and candidate.action == 'create':
                actions.append(BriefingAction(f'📅 {idx}번 일정 제안', f'@mailtoken:{token}:schedule_create'))
            elif candidate and candidate.action == 'update':
                actions.append(BriefingAction(f'🛠 {idx}번 일정 수정', f'@mailtoken:{token}:schedule_update'))
            elif candidate and candidate.action == 'cancel':
                actions.append(BriefingAction(f'🗑 {idx}번 일정 취소', f'@mailtoken:{token}:schedule_cancel'))
    if not actions:
        return None
    return build_inline_keyboard(actions, row_size=1)
