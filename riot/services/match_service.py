from riot.models.match.match import Match
from riot.models.match.metadata import Metadata
from riot.models.match.info import Info
from riot.models.match.teams import Team
from riot.models.match.ban import Ban
from riot.models.match.objetive import Objective
from riot.models.match.objetives import Objectives
from typing import List, Optional
from riot.core.api_client import APIClient
from riot.models.match.match import Match
from riot.models.match.metadata import Metadata
from riot.models.match.info import Info
from riot.models.match.perks import PerkSelection, PerkStyle, Perks
from riot.models.match.participants import Participant
from riot.models.match.challenges import Challenges


class MatchService:
    def __init__(self, region: str):
        self.client = APIClient(region)

    def get_match_ids_by_puuid(self, puuid: str, start: int = 0, count: int = 20,
                               startTime: Optional[int] = None, endTime: Optional[int] = None,
                               queue: Optional[int] = None, type: Optional[str] = None) -> Optional[List[str]]:
        params = {
            "start": start,
            "count": count,
        }
        if startTime:
            params["startTime"] = startTime
        if endTime:
            params["endTime"] = endTime
        if queue:
            params["queue"] = queue
        if type:
            params["type"] = type

        endpoint = f"lol/match/v5/matches/by-puuid/{puuid}/ids"
        url = self.client.get_url("https://{REGION}.api.riotgames.com", endpoint)
        data = self.client.get(url, params=params)
        if isinstance(data, list):
            return data
        return None

    def get_match_by_id(self, match_id: str) -> Optional[Match]:
        endpoint = f"lol/match/v5/matches/{match_id}"
        url = self.client.get_url("https://{REGION}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if isinstance(data, dict):
            metadata = Metadata(
                data_version=data["metadata"]["dataVersion"],
                match_id=data["metadata"]["matchId"],
                participants=data["metadata"]["participants"]
            )

            teams = [
                Team(
                    team_id=team_data["teamId"],
                    win=team_data["win"],
                    bans=[Ban(ban["championId"], ban["pickTurn"]) for ban in team_data["bans"]],
                    objectives=Objectives(
                        baron=Objective(**team_data["objectives"]["baron"]),
                        champion=Objective(**team_data["objectives"]["champion"]),
                        dragon=Objective(**team_data["objectives"]["dragon"]),
                        horde=Objective(**team_data["objectives"]["horde"]),
                        inhibitor=Objective(**team_data["objectives"]["inhibitor"]),
                        rift_herald=Objective(**team_data["objectives"]["riftHerald"]),
                        tower=Objective(**team_data["objectives"]["tower"])
                    )
                ) for team_data in data["info"]["teams"]
            ]

            participants = [
                Participant(
                    participant_id=participant_data["participantId"],
                    team_id=participant_data["teamId"],
                    champion_id=participant_data["championId"],
                    champion_name=participant_data["championName"],
                    role=participant_data["role"],
                    lane=participant_data["lane"],
                    summoner_name=participant_data.get("summonerName", ""),
                    summoner_id=participant_data["summonerId"],
                    summoner_level=participant_data["summonerLevel"],
                    summoner1_id=participant_data["summoner1Id"],
                    summoner2_id=participant_data["summoner2Id"],
                    kills=participant_data["kills"],
                    deaths=participant_data["deaths"],
                    assists=participant_data["assists"],
                    gold_earned=participant_data["goldEarned"],
                    gold_spent=participant_data["goldSpent"],
                    total_damage_dealt=participant_data["totalDamageDealt"],
                    total_damage_dealt_to_champions=participant_data["totalDamageDealtToChampions"],
                    total_damage_taken=participant_data["totalDamageTaken"],
                    total_minions_killed=participant_data["totalMinionsKilled"],
                    time_played=participant_data["timePlayed"],
                    win=participant_data["win"],
                    perks=Perks(
                        stat_perks=participant_data["perks"]["statPerks"],
                        styles=[
                            PerkStyle(
                                description=style["description"],
                                selections=[PerkSelection(**selection) for selection in style["selections"]],
                                style=style["style"]
                            ) for style in participant_data["perks"]["styles"]
                        ]
                    ),
                    challenges=Challenges(**participant_data["challenges"])
                ) for participant_data in data["info"]["participants"]
            ]

            info = Info(
                game_creation=data["info"]["gameCreation"],
                game_duration=data["info"]["gameDuration"],
                game_end_timestamp=data["info"]["gameEndTimestamp"],
                game_id=data["info"]["gameId"],
                game_mode=data["info"]["gameMode"],
                game_name=data["info"]["gameName"],
                game_start_timestamp=data["info"]["gameStartTimestamp"],
                game_type=data["info"]["gameType"],
                game_version=data["info"]["gameVersion"],
                map_id=data["info"]["mapId"],
                platform_id=data["info"]["platformId"],
                queue_id=data["info"]["queueId"],
                tournament_code=data["info"]["tournamentCode"],
                end_of_game_result=data["info"]["endOfGameResult"],
                participants=participants,
                teams=teams
            )

            match = Match(metadata=metadata, info=info)
            return match
        return None

    def get_match_timeline_by_id(self, match_id: str) -> Optional[dict]:
        pass
