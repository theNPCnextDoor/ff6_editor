from dataclasses import dataclass, field
from typing import List

from src.utils import Ips
from src.utils.release_notes.contributor import Contributor
from src.utils.release_notes.version import Version


@dataclass
class ReleaseNotes:
    LINE_WIDTH = 80
    title: str
    author: str
    version_history: List[Version]
    ips: Ips
    description: str
    how_to_use: str
    applies_to: List[Game] = field(default_factory=list)
    credits: List[Contributor] = field(default_factory=list)

    def __str__(self):
        return (
            f"Title: {self.title}\n"
            f"Author: {self.author}\n"
            f"Version: {self.version_history[-1]}\n"
        )
