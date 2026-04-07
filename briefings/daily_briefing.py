from __future__ import annotations

from command_router import run_command
from intent_parser import Intent
from briefings.response_formatter import format_summary


def build_daily_briefing() -> str:
    result = run_command(Intent(action='summary', important_only=True, date_filter='today', limit=10))
    if isinstance(result, str):
        return result
    if not result:
        return '오늘 온 메일이 없거나 조건에 맞는 메일이 없습니다.'
    return format_summary(result)


if __name__ == '__main__':
    print(build_daily_briefing())
