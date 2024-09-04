from typing import Optional
from riot.core.api_client import APIClient
from riot.models.summoner import Summoner


class SummonerService:
    def __init__(self, region: str):
        self.client = APIClient(region)

    def get_summoner_by_puuid(self) -> Optional[Summoner]:
        pass

    def get_summoner_by_account_id(self) -> Optional[Summoner]:
        pass

    def get_summoner_by_summoner_id(self) -> Optional[Summoner]:
        pass

    def get_summoner_by_access_token(self) -> Optional[Summoner]:
        pass
