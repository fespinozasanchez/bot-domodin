from riot.core.api_client import APIClient
from riot.models.league import LeagueEntry
from typing import Optional, List


class LeagueService:
    def __init__(self, region: str):
        self.client = APIClient(region)

    def get_ranked_info_by_summoner_id(self, summoner_id: str) -> Optional[List[LeagueEntry]]:
        endpoint = f"lol/league/v4/entries/by-summoner/{summoner_id}"
        url = self.client.get_url(f"https://{self.client.region}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if data:
            return [LeagueEntry(**entry) for entry in data]
        return None
