from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Version:
    major: int
    minor: int
    release_date: datetime
    changes: List[str]
