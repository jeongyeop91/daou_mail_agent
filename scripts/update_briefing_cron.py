from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON_BIN = subprocess.check_output(['which', 'python3'], text=True).strip()
LOG_FILE = ROOT / 'data' / 'briefing_cron.log'
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

lines = [
    f"0 9 * * * cd {ROOT} && {PYTHON_BIN} scripts/send_workday_briefing.py >> {LOG_FILE} 2>&1",
    f"0 11 * * * cd {ROOT} && {PYTHON_BIN} scripts/send_mail_briefing.py >> {LOG_FILE} 2>&1",
    f"0 16 * * * cd {ROOT} && {PYTHON_BIN} scripts/send_mail_briefing.py >> {LOG_FILE} 2>&1",
]

try:
    existing = subprocess.check_output(['crontab', '-l'], text=True)
except subprocess.CalledProcessError:
    existing = ''

filtered = []
for line in existing.splitlines():
    if 'scripts/poll_mail_workflow.py' in line:
        continue
    if 'scripts/send_workday_briefing.py' in line:
        continue
    if 'scripts/send_mail_briefing.py' in line:
        continue
    filtered.append(line)

content = '\n'.join([*filtered, *lines]).strip() + '\n'
subprocess.run(['crontab', '-'], input=content, text=True, check=True)
print(content)
