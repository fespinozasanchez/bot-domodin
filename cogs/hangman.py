import random
from discord.ext import commands


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
        await ctx.send("¡El juego del ahorcado ha comenzado!\nAdivina la palabra: " + " ".join(self.games[ctx.channel.id]["state"]))

    @commands.command(help="Adivina una letra o la palabra completa en el juego de ahorcado.")
    async def adivinar(self, ctx, guess: str):
        if ctx.channel.id not in self.games:
            await ctx.send("No hay ningún juego de ahorcado en curso. Usa `!ahorcado` para comenzar uno.")
            return

        game = self.games[ctx.channel.id]
        guess = guess.lower()

        # Check if the guess is a single letter
        if len(guess) == 1:
            if guess in game["guessed_letters"]:
                await ctx.send(f"Ya has adivinado la letra '{guess}'. Intenta con otra.")
                return

            game["guessed_letters"].append(guess)

            if guess in game["word"]:
                for idx, char in enumerate(game["word"]):
                    if char == guess:
                        game["state"][idx] = guess
                if "_" not in game["state"]:
                    await ctx.send("¡Felicidades! Has adivinado la palabra: " + game["word"])
                    del self.games[ctx.channel.id]
                else:
                    await ctx.send(" ".join(game["state"]))
            else:
                game["failures"] += 1
                if game["failures"] >= 6:
                    await ctx.send(f"Lo siento, has perdido. La palabra era: {game['word']}")
                    del self.games[ctx.channel.id]
                else:
                    await ctx.send(f"Letra incorrecta. Intentos fallidos: {game['failures']}/6\n" + " ".join(game["state"]))

        # Check if the guess is a full word
        else:
            if guess == game["word"]:
                await ctx.send("¡Felicidades! Has adivinado la palabra: " + game["word"])
                del self.games[ctx.channel.id]
            else:
                game["failures"] += 1
                if game["failures"] >= 6:
                    await ctx.send(f"Lo siento, has perdido. La palabra era: {game['word']}")
                    del self.games[ctx.channel.id]
                else:
                    await ctx.send(f"Palabra incorrecta. Intentos fallidos: {game['failures']}/6\n" + " ".join(game["state"]))

    @commands.command(help="Muestra el estado actual del juego de ahorcado.")
    async def estado(self, ctx):
        if ctx.channel.id not in self.games:
            await ctx.send("No hay ningún juego de ahorcado en curso. Usa `!ahorcado` para comenzar uno.")
            return

        game = self.games[ctx.channel.id]
        await ctx.send("Estado actual: " + " ".join(game["state"]) + f"\nIntentos fallidos: {game['failures']}/6")

    @commands.command(help="Termina el juego de ahorcado actual.")
    async def terminar(self, ctx):
        if ctx.channel.id in self.games:
            del self.games[ctx.channel.id]
            await ctx.send("El juego de ahorcado ha sido terminado.")
        else:
            await ctx.send("No hay ningún juego de ahorcado en curso.")


async def setup(bot):
    await bot.add_cog(Hangman(bot))
