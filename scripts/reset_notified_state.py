from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / 'data' / 'mail_cache.db'


def main() -> None:
    if not DB_PATH.exists():
        print('DB_MISSING')
        return
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute('UPDATE messages SET notified_at = NULL')
        print(f'RESET={result.rowcount}')


if __name__ == '__main__':
    main()
