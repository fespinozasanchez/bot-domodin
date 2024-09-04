from typing import List, Optional
from riot.core.api_client import APIClient
from riot.models.mastery import ChampionMastery


class MasteryService:
    def __init__(self, region: str):
        self.client = APIClient(region)

    def get_all_masteries_by_puuid(self, puuid: str) -> Optional[List[ChampionMastery]]:
        endpoint = f"lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        url = self.client.get_url("https://{REGION}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if isinstance(data, list):
            return [ChampionMastery(**item) for item in data]
        return None

    def get_mastery_by_puuid_and_champion(self, puuid: str, champion_id: int) -> Optional[ChampionMastery]:
        endpoint = f"lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}"
        url = self.client.get_url("https://{REGION}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        print(url)
        if isinstance(data, dict):
            return ChampionMastery(**data)
        return None

    def get_total_mastery_score(self, puuid: str) -> Optional[int]:
        endpoint = f"lol/champion-mastery/v4/scores/by-puuid/{puuid}"
        url = self.client.get_url("https://{REGION}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if isinstance(data, int):
            return data
        return None
