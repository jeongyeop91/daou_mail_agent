from __future__ import annotations

from agents.collector import fetch_recent_emails
from agents.classifier import classify_email
from briefing_actions import BriefingAction
from briefings.calendar_briefing import fetch_calendar_events
from category_rules import categorize_email
from briefings.tasks_briefing import _fetch_tasks


DEFAULT_NEXT_ACTIONS = [
    BriefingAction('📮 최근 메일', '최근 메일 5개 보여줘'),
    BriefingAction('📅 오늘 일정', '오늘 일정 뭐야?'),
    BriefingAction('✅ 전체 할 일', '전체 할 일 보여줘'),
]


def get_workday_next_actions(has_important_mail: bool = True, has_events: bool = True, has_tasks: bool = True) -> list[BriefingAction]:
    actions: list[BriefingAction] = []
    if has_important_mail:
        actions.append(BriefingAction('📮 우선 메일 목록', '최근 메일 5개 보여줘'))
    if has_events:
        actions.append(BriefingAction('📅 오늘 일정 확인', '오늘 일정 뭐야?'))
    if has_tasks:
        actions.append(BriefingAction('✅ 할 일 확인', '전체 할 일 보여줘'))

    fallback_pool = [
        BriefingAction('📮 최근 메일', '최근 메일 5개 보여줘'),
        BriefingAction('📝 답장 필요 메일', '답장 필요한 메일 브리핑해줘'),
        BriefingAction('📅 오늘 일정 확인', '오늘 일정 뭐야?'),
        BriefingAction('✅ 전체 할 일', '전체 할 일 보여줘'),
    ]
    seen = {action.command for action in actions}
    for action in fallback_pool:
        if len(actions) >= 3:
            break
        if action.command not in seen:
            actions.append(action)
            seen.add(action.command)
    return actions or DEFAULT_NEXT_ACTIONS.copy()


def build_workday_briefing() -> str:
    emails = fetch_recent_emails(limit=10)
    important = [e for e in emails if classify_email(e) == '중요'][:3]
    events = fetch_calendar_events('today')
    tasks = [t for t in _fetch_tasks('today') if t.get('status') != 'completed']

    actions = get_workday_next_actions(
        has_important_mail=bool(important),
        has_events=bool(events),
        has_tasks=bool(tasks),
    )

    lines = [
        '📮 오늘 업무 브리핑',
        '━━━━━━━━━━',
        '한눈 요약',
        f'🔴 중요 메일 {len(important)}건',
        f'🔵 오늘 일정 {len(events)}건',
        f'🟡 오늘 할 일 {len(tasks)}건',
        '',
        '현재 상태',
        '오늘 확인이 필요한 메일, 일정, 할 일을 한 번에 정리했습니다.',
        '우선순위가 높은 항목부터 순서대로 확인하실 수 있도록 구성했습니다.',
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
    else:
        lines.extend(['', '━━━━━━━━━━', '우선 확인 메일', '현재 우선 확인으로 분류된 메일은 없습니다.'])

    lines.extend(['', '━━━━━━━━━━', '오늘 일정'])
    if events:
        for idx, event in enumerate(events[:3], start=1):
            start = (event.get('start') or {}).get('dateTime') or (event.get('start') or {}).get('date') or ''
            lines.append(f'{idx}. {event.get("summary")}')
            lines.append(f'시간: {start}')
    else:
        lines.append('등록된 일정이 없습니다.')

    lines.extend(['', '━━━━━━━━━━', '오늘 할 일'])
    if tasks:
        for idx, task in enumerate(tasks[:3], start=1):
            lines.append(f'{idx}. {task.get("title")}')
            if task.get('due'):
                lines.append(f'기한: {task.get("due")}')
    else:
        lines.append('등록된 할 일이 없습니다.')

    lines.extend(['', '━━━━━━━━━━', '권장 다음 액션'])
    for idx, action in enumerate(actions, start=1):
        lines.append(f'{idx}) {action.command}')
    return '\n'.join(lines)
