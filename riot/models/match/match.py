from typing import List, Dict

from riot.models.match.metadata import Metadata
from riot.models.match.info import Info


class Match:
    def __init__(self, metadata: Metadata, info: Dict):
        self.metadata: Metadata = metadata
        self.info: Info = info

    def __repr__(self) -> str:
        return f"<Match ID={self.metadata.match_id}>"

    def __str__(self) -> str:
        return f"Match(Metadata={self.metadata}, Info={self.info})"
