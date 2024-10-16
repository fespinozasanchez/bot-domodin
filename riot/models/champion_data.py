# models/champion.py

import requests


class ChampionData:
    def __init__(self, version='14.17.1'):
        self.version = version
        self.champion_id_to_name = self._load_champion_data()

    def _load_champion_data(self):

        url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/data/es_AR/champion.json"
        response = requests.get(url)
        data = response.json()
        champion_id_to_name = {}

        for champion_name, champion_data in data['data'].items():
            champion_id = int(champion_data['key'])  # 'key' es el ID del campeón como string
            champion_id_to_name[champion_id] = champion_name

        return champion_id_to_name

    def get_champion_name(self, champion_id):
        return self.champion_id_to_name.get(champion_id, "Unknown")

    def get_champion_image_url(self, champion_id):
        champion_name = self.get_champion_name(champion_id)
        if champion_name == "Unknown":
            return None
        return f"https://ddragon.leagueoflegends.com/cdn/{self.version}/data/es_AR/{champion_name}.json"
