from typing import List, Optional
from riot.core.api_client import APIClient
from riot.models.spectator import CurrentGameInfo, FeaturedGame


class SpectatorService:
    def __init__(self, region: str):
        self.client = APIClient(region)

    def get_current_game_by_summoner(self, summoner_id: str) -> Optional[CurrentGameInfo]:
        endpoint = f"lol/spectator/v5/active-games/by-summoner/{summoner_id}"
        url = self.client.get_url("https://{REGION}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if isinstance(data, dict):
            return CurrentGameInfo(**data)
        return None

    def get_featured_games(self) -> Optional[List[FeaturedGame]]:
        endpoint = "lol/spectator/v5/featured-games"
        url = self.client.get_url("https://{REGION}.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if isinstance(data, dict) and 'gameList' in data:
            return [FeaturedGame(**game) for game in data['gameList']]
        return None
