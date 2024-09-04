from typing import List, Optional

from riot.models.match.teams import Team


class Info:
    def __init__(self,
                 game_creation: int,
                 game_duration: int,
                 game_end_timestamp: int,
                 game_id: int,
                 game_mode: str,
                 game_name: str,
                 game_start_timestamp: int,
                 game_type: str,
                 game_version: str,
                 map_id: int,
                 platform_id: str,
                 queue_id: int,
                 tournament_code: str,
                 end_of_game_result: str,
                 participants: Optional[List[dict]] = None,
                 teams: Optional[List[Team]] = None):
        self.game_creation: int = game_creation
        self.game_duration: int = game_duration
        self.game_end_timestamp: int = game_end_timestamp
        self.game_id: int = game_id
        self.game_mode: str = game_mode
        self.game_name: str = game_name
        self.game_start_timestamp: int = game_start_timestamp
        self.game_type: str = game_type
        self.game_version: str = game_version
        self.map_id: int = map_id
        self.platform_id: str = platform_id
        self.queue_id: int = queue_id
        self.tournament_code: str = tournament_code
        self.end_of_game_result: str = end_of_game_result
        self.participants: Optional[List[dict]] = participants or []
        self.teams: Optional[List[Team]] = teams or []

    def __repr__(self) -> str:
        return f"<Info GameID={self.game_id}, Mode={self.game_mode}, Type={self.game_type}>"

    def __str__(self) -> str:
        teams_str = ", ".join([str(team) for team in self.teams])
        return (f"Info(GameID={self.game_id}, Mode={self.game_mode}, Type={self.game_type}, "
                f"Duration={self.game_duration}s, Version={self.game_version}, MapID={self.map_id}, "
                f"ParticipantsCount={len(self.participants)}, Teams=[{teams_str}])")
