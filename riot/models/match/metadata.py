from typing import List


class Metadata:
    def __init__(self, data_version: str, match_id: str, participants: List[str]):
        self.data_version: str = data_version
        self.match_id: str = match_id
        self.participants: List[str] = participants

    def __repr__(self) -> str:
        return f"<Metadata MatchID={self.match_id}, DataVersion={self.data_version}>"

    def __str__(self) -> str:
        participants_str = ", ".join(self.participants)
        return (f"Metadata(DataVersion={self.data_version}, MatchID={self.match_id}, "
                f"Participants=[{participants_str}])")
