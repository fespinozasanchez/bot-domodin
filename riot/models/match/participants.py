from typing import Optional

from riot.models.match.perks import Perks
from riot.models.match.challenges import Challenges


class Participant:
    def __init__(self,
                 participant_id: int,
                 team_id: int,
                 champion_id: int,
                 champion_name: str,
                 role: str,
                 lane: str,
                 summoner_name: str,
                 summoner_id: str,
                 summoner_level: int,
                 summoner1_id: int,
                 summoner2_id: int,
                 kills: int,
                 deaths: int,
                 assists: int,
                 gold_earned: int,
                 gold_spent: int,
                 total_damage_dealt: int,
                 total_damage_dealt_to_champions: int,
                 total_damage_taken: int,
                 total_minions_killed: int,
                 time_played: int,
                 win: bool,
                 perks: Optional[Perks] = None,
                 challenges: Optional[Challenges] = None):
        self.participant_id: int = participant_id
        self.team_id: int = team_id
        self.champion_id: int = champion_id
        self.champion_name: str = champion_name
        self.role: str = role
        self.lane: str = lane
        self.summoner_name: str = summoner_name
        self.summoner_id: str = summoner_id
        self.summoner_level: int = summoner_level
        self.summoner1_id: int = summoner1_id
        self.summoner2_id: int = summoner2_id
        self.kills: int = kills
        self.deaths: int = deaths
        self.assists: int = assists
        self.gold_earned: int = gold_earned
        self.gold_spent: int = gold_spent
        self.total_damage_dealt: int = total_damage_dealt
        self.total_damage_dealt_to_champions: int = total_damage_dealt_to_champions
        self.total_damage_taken: int = total_damage_taken
        self.total_minions_killed: int = total_minions_killed
        self.time_played: int = time_played
        self.win: bool = win
        self.perks: Optional[Perks] = perks
        self.challenges: Optional[Challenges] = challenges

    def __repr__(self) -> str:
        return f"<Participant ID={self.participant_id}, Champion={self.champion_name}, KDA={self.kills}/{self.deaths}/{self.assists}>"

    def __str__(self) -> str:
        return (f"Participant(ID={self.participant_id}, Champion={self.champion_name}, "
                f"KDA={self.kills}/{self.deaths}/{self.assists}, Role={self.role}, Lane={self.lane}, "
                f"Gold Earned={self.gold_earned}, Total Damage Dealt={self.total_damage_dealt}, "
                f"Challenges={self.challenges})")
