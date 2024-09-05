from riot.core.api_client import APIClient
from riot.models.summoner import Summoner
from typing import Optional


class SummonerService:
    def __init__(self, region: str):
        self.client = APIClient(region)

    def get_summoner_by_puuid(self, puuid: str) -> Optional[Summoner]:
        """
        Obtiene información de un invocador utilizando su PUUID.
        """
        endpoint = f"lol/summoner/v4/summoners/by-puuid/{puuid}"
        url = self.client.get_url(f"https://{self.client.region}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if data:
            return Summoner(**data)
        return None
