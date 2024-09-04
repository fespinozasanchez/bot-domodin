# services/champion_service.py

from riot.models.champion_data import ChampionData


class ChampionService:
    def __init__(self, version='14.17.1'):
        self.champion_data = ChampionData(version)

    def get_champion_name(self, champion_id):
        return self.champion_data.get_champion_name(champion_id)

    def get_champion_image_url(self, champion_id):
        return self.champion_data.get_champion_image_url(champion_id)
