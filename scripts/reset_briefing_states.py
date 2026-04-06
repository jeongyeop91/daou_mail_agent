from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'data' / 'mail_cache.db'


def main() -> None:
    if not DB_PATH.exists():
        print('DB_MISSING')
        return
    with sqlite3.connect(DB_PATH) as conn:
        result = conn.execute('UPDATE messages SET notified_at = NULL, briefed_at = NULL')
        print(f'RESET={result.rowcount}')


if __name__ == '__main__':
    main()
