from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from storage.mail_cache import get_cached_recent, init_mail_cache


def main() -> None:
    init_mail_cache()
    rows = get_cached_recent(10)
    print(f'CACHED={len(rows)}')
    for idx, row in enumerate(rows, start=1):
        flags = []
        if row['is_important']:
            flags.append('중요')
        if row['needs_reply']:
            flags.append('답장필요')
        flag_text = f" [{' / '.join(flags)}]" if flags else ''
        print(f"{idx}. {row['subject']} | {row['sender']} | {row['received_at'] or row['raw_date']} | {row['source_kind']} | {row['classification']}{flag_text}")


if __name__ == '__main__':
    main()
