from __future__ import annotations

from agents.collector import fetch_unread_emails
from agents.classifier import classify_email
from calendar_briefing import fetch_calendar_events
from category_rules import categorize_email
from tasks_briefing import _fetch_tasks


def build_workday_briefing() -> str:
    emails = fetch_unread_emails(limit=5)
    important = [e for e in emails if classify_email(e) == '중요'][:3]
    events = fetch_calendar_events('today')
    tasks = [t for t in _fetch_tasks('today') if t.get('status') != 'completed']

    lines = [
        '📮 오늘 업무 브리핑',
        '━━━━━━━━━━',
        '한눈 요약',
        f'🔴 중요 메일 {len(important)}건',
        f'🔵 오늘 일정 {len(events)}건',
        f'🟡 오늘 할 일 {len(tasks)}건',
    ]

    if important:
        lines.extend(['', '━━━━━━━━━━', '우선 확인 메일'])
        for idx, email in enumerate(important, start=1):
            lines.append(f'{idx}. [{categorize_email(email)}] {email.subject}')
            lines.append(f'보낸 사람: {email.sender}')
            lines.append('우선 확인이 필요한 항목으로 분류되어 먼저 살펴보시는 것을 권장드립니다.')
            lines.append('')
        if lines[-1] == '':
            lines.pop()

    if events:
        lines.extend(['', '━━━━━━━━━━', '오늘 일정'])
        for event in events[:2]:
            lines.append(f'- {event.get("summary")}')

    if tasks:
        lines.extend(['', '오늘 할 일'])
        for task in tasks[:2]:
            lines.append(f'- {task.get("title")}')

    lines.extend([
        '',
        '━━━━━━━━━━',
        '현재 상태 요약',
        '기본 메일 처리 흐름과 업무 브리핑 기능은 확인 가능한 상태입니다.',
        '우선 메일 확인 후 일정과 할 일을 함께 정리하는 방식으로 활용하실 수 있습니다.',
        '',
        '바로 하기',
        '1번 메일 자세히 보여줘',
        '오늘 일정 뭐야?',
        '전체 할 일 보여줘',
    ])
    return '\n'.join(lines)
