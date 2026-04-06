from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from mail_cache import get_cached_reply_needed_emails


def main() -> None:
    emails = get_cached_reply_needed_emails(10)
    print(f'REPLY_NEEDED={len(emails)}')
    for idx, email in enumerate(emails, start=1):
        print(f'{idx}. {email.subject} | {email.sender} | {email.date}')


if __name__ == '__main__':
    main()
