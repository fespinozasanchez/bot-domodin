
import discord
from discord.ext import commands
from riot.services.spectator_service import SpectatorService
from riot.services.account_service import AccountService
from riot.services.mastery_service import MasteryService
from riot.services.spectator_service import SpectatorService
from riot.services.match_service import MatchService


def main():
    region = "la2"
    spectator_service = SpectatorService(region)
    account_service = AccountService()
    mastery_service = MasteryService(region)
    spectator_service = SpectatorService(region)
    match_service = MatchService("americas")

    # # Ejemplo de uso
    puuid = account_service.get_account_by_riot_id("XPegasoX", "LAS").puuid
    spectator_data = spectator_service.get_current_game_by_summoner(puuid)

    # print(puuid)
    # masterie_champ = mastery_service.get_mastery_by_puuid_and_champion(puuid, 2)
    # print(masterie_champ)
    # masteries = mastery_service.get_total_mastery_score(puuid)
    # print(masteries)
    # spectator = spectator_service.get_current_game_by_summoner(puuid)
    # print(str(spectator))
    # matchs = match_service.get_match_ids_by_puuid(puuid)
    # print(matchs)
    # match = match_service.get_match_by_id(matchs[0])
    print(spectator_data)


if __name__ == '__main__':
    main()
