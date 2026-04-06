from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from agents.collector import fetch_recent_emails


def main() -> None:
    items = fetch_recent_emails(limit=5)
    print(f'FETCHED={len(items)}')


if __name__ == '__main__':
    main()
