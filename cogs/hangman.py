import random
from discord.ext import commands
import discord
from utils.data_manager import load_user_data, save_user_data


class Hangman(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command(help="Inicia un nuevo juego de ahorcado.")
    async def ahorcado(self, ctx):
        words = ["python", "discord", "ahorcado",
                 "bot", "programacion", "ingeniero"]
        word = random.choice(words)
        self.games[ctx.channel.id] = {
            "word": word,
            "state": ["_" for _ in word],
            "failures": 0,
            "guessed_letters": []
        }
        embed = discord.Embed(
            title="¡El juego del ahorcado ha comenzado!",
            description="Adivina la palabra:\n```\n" +
            " ".join(self.games[ctx.channel.id]["state"]) + "\n```"
        )
        await ctx.send(embed=embed)

    @commands.command(help="Adivina una letra o la palabra completa en el juego de ahorcado.")
    async def adivinar(self, ctx, guess: str):
        if ctx.channel.id not in self.games:
            await ctx.send("No hay ningún juego de ahorcado en curso. Usa `!ahorcado` para comenzar uno.")
            return

        game = self.games[ctx.channel.id]
        guess = guess.lower()

        if len(guess) == 1:  # Adivinando una letra
            if guess in game["guessed_letters"]:
                await ctx.send(f"Ya has adivinado la letra '{guess}'. Intenta con otra.")
                return

            game["guessed_letters"].append(guess)

            if guess in game["word"]:
                for idx, char in enumerate(game["word"]):
                    if char == guess:
                        game["state"][idx] = guess
                if "_" not in game["state"]:
                    await self._ganar(ctx, game["word"])
                else:
                    embed = discord.Embed(
                        description="```\n" + " ".join(game["state"]) + "\n```"
                    )
                    await ctx.send(embed=embed)
            else:
                await self._fallo(ctx, game)
        else:  # Adivinando una palabra completa
            if guess == game["word"]:
                await self._ganar(ctx, game["word"])
            else:
                await self._fallo(ctx, game)

    @commands.command(help="Muestra el estado actual del juego de ahorcado.")
    async def estado(self, ctx):
        if ctx.channel.id not in self.games:
            await ctx.send("No hay ningún juego de ahorcado en curso. Usa `!ahorcado` para comenzar uno.")
            return

        game = self.games[ctx.channel.id]
        embed = discord.Embed(
            title="Estado actual",
            description="```\n" + " ".join(game["state"]) + "\n```" +
            f"\nIntentos fallidos: {game['failures']}/6"
        )
        await ctx.send(embed=embed)

    @commands.command(help="Termina el juego de ahorcado actual.")
    async def terminar(self, ctx):
        if ctx.channel.id in self.games:
            del self.games[ctx.channel.id]
            await ctx.send("El juego de ahorcado ha sido terminado.")
        else:
            await ctx.send("No hay ningún juego de ahorcado en curso.")

    async def _ganar(self, ctx, word):
        embed = discord.Embed(
            title="¡Felicidades!",
            description="Has adivinado la palabra: " + word,
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

        # Otorgar MelladoCoins al usuario
        user_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        user_data = load_user_data(user_id, guild_id)
        if user_data:
            user_data['balance'] += 50  # Otorgar 50 MelladoCoins
            save_user_data(user_id, guild_id, user_data['balance'])
            await ctx.send(f'{ctx.author.name}, has ganado 50 MelladoCoins. Tu nuevo saldo es {user_data["balance"]} MelladoCoins.')

        del self.games[ctx.channel.id]

    async def _fallo(self, ctx, game):
        game["failures"] += 1
        if game["failures"] >= 6:
            embed = discord.Embed(
                title="Lo siento, has perdido.",
                description=f"La palabra era: {game['word']}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            del self.games[ctx.channel.id]
        else:
            embed = discord.Embed(
                title="Letra incorrecta.",
                description=f"Intentos fallidos: {
                    game['failures']}/6\n```\n" + " ".join(game["state"]) + "\n```"
            )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Hangman(bot))
