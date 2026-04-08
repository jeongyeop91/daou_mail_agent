from __future__ import annotations

from briefings.mail_action_builder import build_mail_action_keyboard
from storage.mail_cache import get_cached_schedule_candidate_emails, mark_schedule_proposed
from schedule_mail import extract_schedule_candidate


def build_schedule_recommendation(limit: int = 3) -> tuple[str, list, dict | None]:
    cached = get_cached_schedule_candidate_emails(limit=10, unproposed_only=True)
    candidates = []
    for email in cached:
        parsed = extract_schedule_candidate(email)
        if parsed and parsed.action == 'create':
            candidates.append((email, parsed))
        if len(candidates) >= limit:
            break
    if not candidates:
        return '현재 새롭게 추천할 일정 메일은 없습니다.', [], None

    lines = [
        '📅 일정 등록 추천',
        '━━━━━━━━━━',
        '현재 상태',
        f'- 새 일정 추천: {len(candidates)}건',
        '- 일정 등록이 필요한 후보 메일만 추렸습니다.',
        '',
        '상세 목록',
    ]
    emails = []
    for idx, (email, candidate) in enumerate(candidates, start=1):
        emails.append(email)
        lines.append(f'{idx}. {candidate.title}')
        lines.append(f'일정: {candidate.start_at.strftime("%Y-%m-%d %H:%M")} ~ {candidate.end_at.strftime("%H:%M")}')
        if candidate.location:
            lines.append(f'장소: {candidate.location}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append('권장 조치: 아래 버튼에서 일정 제안을 바로 실행할 수 있습니다.')
        lines.append('')
    return '\n'.join(lines[:-1]), emails, build_mail_action_keyboard(emails, primary='schedule')


def mark_schedule_recommendation_sent(emails: list) -> int:
    return mark_schedule_proposed(emails)
