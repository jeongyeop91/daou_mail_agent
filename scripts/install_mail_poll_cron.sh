#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="$(command -v python3)"
LOG_DIR="$ROOT/data"
LOG_FILE="$LOG_DIR/mail_poll.log"
mkdir -p "$LOG_DIR"

CRON_LINE="*/10 * * * * cd $ROOT && $PYTHON_BIN scripts/poll_mail_workflow.py >> $LOG_FILE 2>&1"

EXISTING="$(crontab -l 2>/dev/null || true)"
UPDATED="$(printf '%s\n' "$EXISTING" | grep -v 'scripts/poll_mail_workflow.py' || true)"
{
  if [ -n "$UPDATED" ]; then
    printf '%s\n' "$UPDATED"
  fi
  printf '%s\n' "$CRON_LINE"
} | crontab -

echo "Installed cron: $CRON_LINE"
