from __future__ import annotations

from datetime import datetime, timedelta


def _sample_events() -> list[dict]:
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    return [
        {'id': 'evt-1', 'summary': '주간 회의', 'start': {'dateTime': f'{today}T10:00:00+09:00'}},
        {'id': 'evt-2', 'summary': '고객 미팅', 'start': {'dateTime': f'{today}T14:00:00+09:00'}},
        {'id': 'evt-3', 'summary': '내일 일정 샘플', 'start': {'dateTime': f'{tomorrow}T11:00:00+09:00'}},
    ]


def fetch_calendar_events(mode: str = 'today') -> list[dict]:
    events = _sample_events()
    if mode == 'tomorrow':
        return events[2:]
    if mode == 'week':
        return events
    return events[:2]


def build_calendar_briefing(mode: str = 'today') -> str:
    label = {'today': '오늘', 'tomorrow': '내일', 'week': '이번 주'}.get(mode, '오늘')
    events = fetch_calendar_events(mode)
    lines = [f'📅 {label} 일정 브리핑', '━━━━━━━━━━', f'{label} 일정 = {len(events)}건', '']
    for idx, event in enumerate(events, start=1):
        start = (event.get('start') or {}).get('dateTime') or (event.get('start') or {}).get('date') or ''
        lines.append(f'{idx}. {event.get("summary") or "(제목 없음)"}')
        lines.append(f'시간: {start}')
        lines.append('')
    return '\n'.join(lines[:-1] if lines and lines[-1] == '' else lines)
