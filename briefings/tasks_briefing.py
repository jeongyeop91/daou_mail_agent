from __future__ import annotations

from datetime import datetime, timedelta


def _fetch_tasks(mode: str = 'today') -> list[dict]:
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    items = [
        {'title': '제안서 수정본 검토', 'due': today, 'status': 'needsAction'},
        {'title': '회신 초안 작성', 'due': today, 'status': 'needsAction'},
        {'title': '내일 준비 작업', 'due': tomorrow, 'status': 'needsAction'},
    ]
    if mode == 'all':
        return items
    return [item for item in items if item['due'] == today]


def build_tasks_briefing(mode: str = 'today') -> str:
    label = '전체' if mode == 'all' else '오늘'
    tasks = _fetch_tasks(mode)
    active = [t for t in tasks if t.get('status') != 'completed']
    lines = [f'✅ {label} 할 일 브리핑', '━━━━━━━━━━', f'{label} 할 일 = {len(active)}건', '']
    for idx, task in enumerate(active, start=1):
        lines.append(f'{idx}. {task.get("title") or "(제목 없음)"}')
        if task.get('due'):
            lines.append(f'기한: {task.get("due")}')
        lines.append('')
    return '\n'.join(lines[:-1] if lines and lines[-1] == '' else lines)
