from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class EmailItem:
    sender: str
    subject: str
    date: str
    body: str
    has_attachments: bool = False
    parsed_date: datetime | None = None
