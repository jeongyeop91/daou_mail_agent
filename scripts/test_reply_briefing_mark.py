from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from briefings.reply_needed_briefing import build_reply_needed_briefing
from scripts.warm_mail_cache import main as warm_cache
from storage.mail_cache import get_cached_reply_needed_emails


def main() -> None:
    warm_cache()
    before = get_cached_reply_needed_emails(10, unbriefed_only=True)
    print(f'UNBRIEFED_BEFORE={len(before)}')
    print(build_reply_needed_briefing(5))
    after = get_cached_reply_needed_emails(10, unbriefed_only=True)
    print(f'UNBRIEFED_AFTER={len(after)}')


if __name__ == '__main__':
    main()
