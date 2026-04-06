from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from storage.mail_cache import get_cached_reply_needed_emails, mark_briefed


def main() -> None:
    before = get_cached_reply_needed_emails(10, unbriefed_only=True)
    print(f'UNBRIEFED_BEFORE={len(before)}')
    if before:
        marked = mark_briefed(before[:2])
        print(f'MARKED={marked}')
    after = get_cached_reply_needed_emails(10, unbriefed_only=True)
    print(f'UNBRIEFED_AFTER={len(after)}')


if __name__ == '__main__':
    main()
