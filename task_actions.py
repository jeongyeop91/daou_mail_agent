from __future__ import annotations


def add_task(title: str, due_text: str | None = None, notes: str = '') -> str:
    due_part = f' / 기한: {due_text}' if due_text else ''
    note_part = f' / 메모: {notes}' if notes else ''
    return f'할 일을 추가했습니다: {title}{due_part}{note_part}'


def complete_task_by_index(index: int) -> str:
    return f'할 일 {index}번을 완료로 처리했습니다.'


def postpone_task_by_index(index: int, due_text: str) -> str:
    return f'할 일 {index}번 기한을 {due_text} 기준으로 미뤘습니다.'


def delete_task_by_index(index: int) -> str:
    return f'할 일 {index}번을 삭제했습니다.'
