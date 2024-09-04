from riot.core.api_client import APIClient
from riot.models.account import Account


class AccountService:
    def __init__(self):
        self.client = APIClient()

    def get_account_by_puuid(self, puuid):
        endpoint = f"riot/account/v1/accounts/by-puuid/{puuid}"
        url = self.client.get_url("https://americas.api.riotgames.com", endpoint)
        data = self.client.get(url)
        if data:
            return Account(data['puuid'], data['gameName'], data['tagLine'])

    def get_account_by_riot_id(self, gameName, tag):
        endpoint = f"riot/account/v1/accounts/by-riot-id/{gameName}/{tag}"
        url = self.client.get_url("https://americas.api.riotgames.com", endpoint)
        print(url)  # Esto debería mostrar la URL correcta
        data = self.client.get(url)
        if data:
            return Account(data['puuid'], data['gameName'], data['tagLine'])
