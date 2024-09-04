import discord
from discord.ext import commands
from riot.services.champion_service import ChampionService
from riot.services.spectator_service import SpectatorService
from riot.services.account_service import AccountService
from riot.services.mastery_service import MasteryService
from riot.services.match_service import MatchService


class LeageOfLegends(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.region = "la2"
        self.account_service = AccountService()
        self.spectator_service = SpectatorService(self.region)
        self.match_service = MatchService("americas")
        self.mastery_service = MasteryService(self.region)
        self.champion_service = ChampionService()

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
            riot_id, tag = summoner_name.split('#')
            account = self.account_service.get_account_by_riot_id(riot_id, tag)
            summoner_name = account.gameName
            summoner_id = account.puuid

            # Obtener información de la liga
            ranked_data = self.league_service.get_ranked_info_by_summoner_id(summoner_id)

            if not ranked_data:
                await ctx.send(f"{summoner_name} no tiene datos de clasificación.")
                return

            # Crear embed para mostrar el perfil
            embed = discord.Embed(title=f"Perfil de {summoner_name}#{tag}", color=discord.Color.blue())

            # Añadir información de perfil
            for queue in ranked_data:
                embed.add_field(name=f"{queue['queueType']}",
                                value=(
                                    f"División: {queue['tier']} {queue['rank']}\n"
                                    f"Victorias: {queue['wins']}\n"
                                    f"Derrotas: {queue['losses']}\n"
                                    f"Winrate: {round(queue['wins'] / (queue['wins'] + queue['losses']) * 100, 2)}%"
                ),
                    inline=False)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"Ocurrió un error al intentar obtener la información de {summoner_name}. Error: {str(e)}")


async def setup(bot: commands.Bot):
    await bot.add_cog(LeageOfLegends(bot))
