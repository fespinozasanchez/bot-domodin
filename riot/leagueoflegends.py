import discord
from discord.ext import commands
from riot.services.champion_service import ChampionService
from riot.services.spectator_service import SpectatorService
from riot.services.account_service import AccountService
from riot.services.mastery_service import MasteryService
from riot.services.match_service import MatchService
from riot.services.summoner_service import SummonerService
from riot.services.league_service import LeagueService


class LeageOfLegends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.region = "la2"
        self.account_service = AccountService()
        self.spectator_service = SpectatorService(self.region)
        self.match_service = MatchService("americas")
        self.mastery_service = MasteryService(self.region)
        self.champion_service = ChampionService()
        self.summoner_service = SummonerService(self.region)
        self.league_service = LeagueService(self.region)

    @commands.command(name="game")
    async def game(self, ctx, *, summoner_name: str):
        try:
            riot_id, tag = summoner_name.split('#')
            puuid = self.account_service.get_account_by_riot_id(riot_id, tag).puuid
            spectator_data = self.spectator_service.get_current_game_by_summoner(puuid)

            if not spectator_data:
                await ctx.send(f"{summoner_name} no está en una partida.")
                return

            # Convertir la duración del juego a minutos y segundos
            game_duration_minutes = spectator_data.gameLength // 60
            game_duration_seconds = spectator_data.gameLength % 60

            # Determinar la URL de la imagen según el mapId
            map_images = {
                11: "https://pillan.inf.uct.cl/~fespinoza/lol/images/images/img/map/map11.png",
                12: "https://pillan.inf.uct.cl/~fespinoza/lol/images/images/img/map/map12.png",
            }
            map_image_url = map_images.get(spectator_data.mapId, "https://pillan.inf.uct.cl/~fespinoza/lol/images/images/img/map/default.png")

            # Crear embed principal
            embed = discord.Embed(title=f"Partida Actual - {summoner_name}", color=discord.Color.blue())
            embed.set_thumbnail(url=map_image_url)

            # Información del juego
            embed.add_field(name="Juego", value=(
                f"ID: {spectator_data.gameId}\n"
                f"Modo: {spectator_data.gameMode}\n"
                f"Tipo: {spectator_data.gameType}\n"
                f"Duración: {game_duration_minutes}m {game_duration_seconds}s"
            ), inline=False)

            # Separar equipos
            team_100 = [p for p in spectator_data.participants if p.teamId == 100]
            team_200 = [p for p in spectator_data.participants if p.teamId == 200]

            # Formatear equipos para columnas alineadas
            team_100_str = "\n".join(
                [f"{p.riotId} - {self.champion_service.get_champion_name(p.championId)}" for p in team_100]
            )
            team_200_str = "\n".join(
                [f"{p.riotId} - {self.champion_service.get_champion_name(p.championId)}" for p in team_200]
            )

            # Mostrar equipos en dos columnas
            embed.add_field(name="Equipo Azul", value=team_100_str, inline=True)
            embed.add_field(name="Equipo Rojo", value=team_200_str, inline=True)

            await ctx.send(embed=embed)

            # Baneos (en un embed separado)
            if spectator_data.gameMode != "ARAM":
                ban_embed = discord.Embed(title="Baneos en la Partida", color=discord.Color.red())

                banned_champions_blue = [bc for bc in spectator_data.bannedChampions if bc.teamId == 100]
                banned_champions_red = [bc for bc in spectator_data.bannedChampions if bc.teamId == 200]

                banned_blue_str = "\n".join(
                    [f"{self.champion_service.get_champion_name(bc.championId)}" for bc in banned_champions_blue]
                ) or "Ninguno"
                banned_red_str = "\n".join(
                    [f"{self.champion_service.get_champion_name(bc.championId)}" for bc in banned_champions_red]
                ) or "Ninguno"

                # Mostrar baneos en dos columnas
                ban_embed.add_field(name="Baneos Equipo Azul", value=banned_blue_str, inline=True)
                ban_embed.add_field(name="Baneos Equipo Rojo", value=banned_red_str, inline=True)

                await ctx.send(embed=ban_embed)

        except Exception as e:
            await ctx.send(f"Ocurrió un error al intentar obtener la información de {summoner_name}. Error: {str(e)}")

    @commands.command(name="profile")
    async def profile(self, ctx, *, summoner_name: str):
        try:
            # Separar el riot_id y el tag del nombre del invocador
            riot_id, tag = summoner_name.split('#')

            # Obtener la cuenta por Riot ID
            account = self.account_service.get_account_by_riot_id(riot_id, tag)

            if account is None:
                await ctx.send(f"No se encontró información para {summoner_name}.")
                return

            # Obtener el PUUID
            puuid = account.puuid

            # Obtener información del invocador usando el PUUID
            summoner = self.summoner_service.get_summoner_by_puuid(puuid)

            if summoner is None:
                await ctx.send(f"No se encontró información de invocador para {summoner_name}.")
                return

            # Crear embed inicial para mostrar información general del perfil
            embed = discord.Embed(title=f"Perfil de {summoner_name}#{tag}", color=discord.Color.blue())
            embed.add_field(name="Nivel", value=summoner.summonerLevel, inline=True)
            embed.set_thumbnail(url=f"http://ddragon.leagueoflegends.com/cdn/14.17.1/img/profileicon/{summoner.profileIconId}.png")

            # Enviar el primer embed con la información general
            await ctx.send(embed=embed)

            # Obtener las ligas clasificatorias
            ranked_data = self.league_service.get_ranked_info_by_summoner_id(summoner.id)

            # Mapeo de los tiers para imágenes
            tier_images = {
                "IRON": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Iron.png",
                "BRONZE": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Bronze.png",
                "SILVER": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Silver.png",
                "GOLD": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Gold.png",
                "PLATINUM": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Platinum.png",
                "DIAMOND": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Diamond.png",
                "MASTER": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Master.png",
                "GRANDMASTER": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Grandmaster.png",
                "CHALLENGER": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Challenger.png",
                "EMERALD": "https://pillan.inf.uct.cl/~fespinoza/lol/emblems/Rank=Emerald.png"
            }

            # Mapeo para mostrar nombres personalizados en las colas
            queue_names = {
                "RANKED_SOLO_5x5": "SOLOQ",
                "RANKED_FLEX_SR": "FLEX"
            }

            if ranked_data:
                # Crear un embed separado para cada tipo de liga
                for league in ranked_data:
                    # Obtener la URL de la imagen correspondiente al rango
                    rank_image_url = tier_images.get(league.tier.upper(), None)

                    # Obtener el nombre de la cola o usar el valor por defecto si no está en el mapeo
                    queue_name = queue_names.get(league.queueType, league.queueType)

                    league_embed = discord.Embed(title=f"{queue_name}", color=discord.Color.green())
                    league_embed.add_field(name="División", value=f"{league.tier} {league.rank}", inline=True)
                    league_embed.add_field(name="LP", value=f"{league.leaguePoints} LP", inline=True)
                    league_embed.add_field(name="Victorias", value=f"{league.wins}", inline=True)
                    league_embed.add_field(name="Derrotas", value=f"{league.losses}", inline=True)
                    league_embed.add_field(name="Winrate", value=f"{round(league.wins / (league.wins + league.losses) * 100, 2)}%", inline=True)

                    # Agregar la imagen del rango si está disponible
                    if rank_image_url:
                        league_embed.set_thumbnail(url=rank_image_url)

                    # Enviar el embed para cada tipo de clasificación
                    await ctx.send(embed=league_embed)
            else:
                await ctx.send(f"{summoner_name} no tiene datos de clasificación en ninguna cola.")

        except ValueError:
            await ctx.send(f"El formato del nombre de invocador {summoner_name} es incorrecto. Usa Nombre#Etiqueta.")
        except Exception as e:
            await ctx.send(f"Ocurrió un error al intentar obtener la información de {summoner_name}. Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(LeageOfLegends(bot))
