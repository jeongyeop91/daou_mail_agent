from __future__ import annotations

from mail_cache import get_cached_schedule_candidate_emails, mark_schedule_proposed
from schedule_mail import extract_schedule_candidate


def build_schedule_recommendation(limit: int = 3) -> tuple[str, list]:
    cached = get_cached_schedule_candidate_emails(limit=10, unproposed_only=True)
    candidates = []
    for email in cached:
        parsed = extract_schedule_candidate(email)
        if parsed and parsed.action == 'create':
            candidates.append((email, parsed))
        if len(candidates) >= limit:
            break
    if not candidates:
        return '새롭게 추천할 일정 메일이 없습니다.', []

    lines = ['📅 일정 등록 추천', '━━━━━━━━━━', f'추천 일정 = {len(candidates)}건', '']
    emails = []
    for idx, (email, candidate) in enumerate(candidates, start=1):
        emails.append(email)
        lines.append(f'{idx}. {candidate.title}')
        lines.append(f'일정: {candidate.start_at.strftime("%Y-%m-%d %H:%M")} ~ {candidate.end_at.strftime("%H:%M")}')
        if candidate.location:
            lines.append(f'장소: {candidate.location}')
        lines.append(f'보낸 사람: {email.sender}')
        lines.append(f'권장 조치: {idx}번 메일 일정등록 제안해줘')
        lines.append('')
    return '\n'.join(lines[:-1]), emails


def build_and_mark_schedule_recommendation(limit: int = 3) -> str:
    text, emails = build_schedule_recommendation(limit)
    if emails:
        mark_schedule_proposed(emails)
    return text
