from __future__ import annotations


def create_calendar_event(title: str, date_text: str, time_text: str, description: str = '') -> str:
    return f'일정을 등록했습니다: {title} / {date_text} / {time_text}'


def update_calendar_event(event_id: str, summary: str, date_text: str, time_text: str, description: str | None = None) -> str:
    return f'일정을 수정했습니다: {event_id} / {summary} / {date_text} / {time_text}'


def update_calendar_event_by_index(index: int, summary: str, date_text: str, time_text: str, description: str | None = None) -> str:
    return f'{index}번 일정을 수정했습니다: {summary} / {date_text} / {time_text}'


def delete_calendar_event(event_id: str) -> str:
    return f'일정을 삭제했습니다: {event_id}'


def delete_calendar_event_by_index(index: int) -> str:
    return f'{index}번 일정을 삭제했습니다.'
