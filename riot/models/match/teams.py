from typing import List

from riot.models.match.ban import Ban
from riot.models.match.objetives import Objectives


class Team:
    def __init__(self, team_id: int, win: bool, bans: List[Ban], objectives: Objectives):
        self.team_id: int = team_id
        self.win: bool = win
        self.bans: List[Ban] = bans
        self.objectives: Objectives = objectives

    def __repr__(self) -> str:
        return f"<Team ID={self.team_id}, Win={self.win}>"

    def __str__(self) -> str:
        bans_str = ", ".join([str(ban) for ban in self.bans])
        return f"Team(ID={self.team_id}, Win={self.win}, Bans=[{bans_str}], Objectives={self.objectives})"
