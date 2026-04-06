from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BriefingAction:
    label: str
    command: str


def build_inline_keyboard(actions: list[BriefingAction], row_size: int = 2) -> dict:
    rows: list[list[dict]] = []
    current: list[dict] = []
    for action in actions:
        current.append({'text': action.label, 'callback_data': f'cmd:{action.command}'})
        if len(current) >= row_size:
            rows.append(current)
            current = []
    if current:
        rows.append(current)
    return {'inline_keyboard': rows}


def build_reply_keyboard(actions: list[BriefingAction], row_size: int = 2) -> dict:
    rows: list[list[dict]] = []
    current: list[dict] = []
    for action in actions:
        current.append({'text': action.command})
        if len(current) >= row_size:
            rows.append(current)
            current = []
    if current:
        rows.append(current)
    return {
        'keyboard': rows,
        'resize_keyboard': True,
        'one_time_keyboard': False,
        'input_field_placeholder': '추천 액션을 눌러 바로 실행할 수 있습니다',
    }
