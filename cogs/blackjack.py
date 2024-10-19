import logging
import discord
from discord.ext import commands
from discord.ui import Button, View
import random
from cogs.const.map import MAP_CARD, MAP_EMOJIS
from discord import app_commands

from utils.data_manager import load_user_data, save_user_data


class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.values = MAP_CARD
        self.deck = list(self.values.keys()) * 4
        self.emoji_map = MAP_EMOJIS

    def draw_card(self):
        """Draws a random card from the deck."""
        return random.choice(self.deck)

    def calculate_total(self, hand):
        """Calculates the total value of a hand, adjusting for Aces."""
        total = sum(self.values[card] for card in hand)
        ace_count = hand.count('A')
        while total > 21 and ace_count:
            total -= 10
            ace_count -= 1
        return total

    def get_emoji(self, card):
        """Gets the emoji for a specific card based on its rank and suit."""
        if card == "A":
            return self.emoji_map.get("1", ":question:")
        elif card.startswith("A"):  # Otros As
            return self.emoji_map.get(card[1:], ":question:")
        elif card.startswith("J"):  # Jota
            return self.emoji_map.get("J" + card[1:], ":question:")
        elif card.startswith("Q"):  # Reina
            return self.emoji_map.get("Q" + card[1:], ":question:")
        elif card.startswith("K"):  # Rey
            return self.emoji_map.get("K" + card[1:], ":question:")
        else:
            return self.emoji_map.get(card, ":question:")

    @commands.command(name='blackjack', help='Comienza un juego de Blackjack contra el bot. Incluye una apuesta.')
    async def blackjack(self, ctx, amount: str):
        await self._blackjack(ctx, amount)

    @app_commands.command(name='blackjack', description='Comienza un juego de Blackjack contra el bot. Incluye una apuesta.')
    async def slash_blackjack(self, interaction: discord.Interaction, amount: str):
        ctx = await commands.Context.from_interaction(interaction)
        await self._blackjack(ctx, amount)

    async def _blackjack(self, ctx, amount: str):
        """Start a game of Blackjack against the bot with a bet."""
        usuario = ctx.author
        user_id = str(usuario.id)
        guild_id = str(ctx.guild.id)
        bot_user_id = str(self.bot.user.id)
        try:
            bot_data = load_user_data(bot_user_id, guild_id)
            user_data = load_user_data(user_id, guild_id)
        except Exception as e:
            embed = discord.Embed(
                title="🚫 Error de Carga",
                description="Ha ocurrido un error al cargar los datos del usuario.",
                color=discord.Color.red()
            )
            logging.error(f"Error al cargar los datos del usuario: {e}")
            await ctx.send(embed=embed)
            return

        if user_data is None:
            embed = discord.Embed(
                title="🚫 Usuario No Registrado",
                description=f"{usuario.name}, no estás registrado. Usa el comando !registrar para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError("No puedes apostar cantidades negativas o cero.")
        except ValueError:
            embed = discord.Embed(
                title="🚫 Error de Apuesta",
                description=f"{usuario.name}, la apuesta debe ser un número entero.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            logging.error(f"Error al convertir la apuesta a entero.")
            return

        if user_data['balance'] < amount:
            amount_formatted = f"${amount:,.0f}".replace(",", ".")
            balance_formatted = f"${user_data['balance']:,.0f}".replace(",", ".")
            embed = discord.Embed(
                title="🚫 Saldo Insuficiente",
                description=f"{usuario.name}, no tienes suficiente saldo para apostar {amount_formatted} en MelladoJack. Tu saldo actual es {balance_formatted}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        player_hand = [self.draw_card(), self.draw_card()]
        dealer_hand = [self.draw_card(), self.draw_card()]

        player_total = self.calculate_total(player_hand)
        dealer_total = self.calculate_total(dealer_hand)

        player_cards = " ".join(self.get_emoji(card) for card in player_hand)
        dealer_cards = f"{self.get_emoji(dealer_hand[0])} {self.get_emoji('back')}"

        embed = discord.Embed(title="Blackjack", description="¡Comienza el juego de Blackjack!", color=0x00ff00)
        embed.add_field(name=f"{ctx.author.name}", value=f"{player_cards} (Total: {player_total})")
        embed.add_field(name=f"{self.bot.user.name}", value=f"{dealer_cards} (Total: {self.values[dealer_hand[0]]})")
        embed.set_thumbnail(url="https://pillan.inf.uct.cl/~fespinoza/images/blackjack.webp")

        view = BlackjackView(player_hand, dealer_hand, player_total, dealer_total, self, amount, user_data, bot_data, user_id, bot_user_id, guild_id)
        await ctx.send(embed=embed, view=view)


class BlackjackView(View):
    def __init__(self, player_hand, dealer_hand, player_total, dealer_total, cog, amount, user_data, bot_data, user_id, bot_user_id, guild_id):
        super().__init__(timeout=60)
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.player_total = player_total
        self.dealer_total = dealer_total
        self.cog = cog
        self.amount = amount
        self.user_data = user_data
        self.bot_data = bot_data
        self.user_id = user_id
        self.bot_user_id = bot_user_id
        self.guild_id = guild_id

    @discord.ui.button(label="Pedir", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: Button):
        """Player requests another card."""
        new_card = self.cog.draw_card()
        self.player_hand.append(new_card)
        self.player_total = self.cog.calculate_total(self.player_hand)

        if self.player_total > 21:
            self.user_data['balance'] -= self.amount
            self.bot_data['balance'] += self.amount

            save_user_data(self.user_id, self.guild_id, self.user_data['balance'])
            save_user_data(self.bot_user_id, self.guild_id, self.bot_data['balance'])

            amount_formatted = f"${self.amount:,.0f}".replace(",", ".")
            balance_formatted = f"${self.user_data['balance']:,.0f}".replace(",", ".")

            embed = discord.Embed(title="Blackjack", description=f"Te pasaste. Has perdido {amount_formatted} MelladoCoins. Tu nuevo saldo es {balance_formatted} ", color=0xff0000)
            player_cards = " ".join(self.cog.get_emoji(card) for card in self.player_hand)
            dealer_cards = " ".join(self.cog.get_emoji(card) for card in self.dealer_hand)
            embed.add_field(name="Tus cartas", value=f"{player_cards} (Total: {self.player_total})")
            embed.add_field(name="Cartas del bot", value=f"{dealer_cards} (Total: {self.dealer_total})")
            embed.set_thumbnail(url="https://pillan.inf.uct.cl/~fespinoza/images/blackjack.webp")
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(title="Blackjack", description="Tu turno continúa.", color=0x00ff00)
            player_cards = " ".join(self.cog.get_emoji(card) for card in self.player_hand)
            dealer_cards = f"{self.cog.get_emoji(self.dealer_hand[0])} {self.cog.get_emoji('back')}"
            embed.add_field(name="Tus cartas", value=f"{player_cards} (Total: {self.player_total})")
            embed.add_field(name="Cartas del bot", value=f"{dealer_cards} (Total: {self.cog.values[self.dealer_hand[0]]})")
            embed.set_thumbnail(url="https://pillan.inf.uct.cl/~fespinoza/images/blackjack.webp")
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Me planto", style=discord.ButtonStyle.secondary)
    async def stand(self, interaction: discord.Interaction, button: Button):
        """Player stands and the dealer reveals their cards."""
        while self.dealer_total < 17:
            new_card = self.cog.draw_card()
            self.dealer_hand.append(new_card)
            self.dealer_total = self.cog.calculate_total(self.dealer_hand)

        embed = discord.Embed(title="Blackjack", description="El juego ha terminado." if self.dealer_total > 21 else "El bot se planta.", color=discord.Color.blue())
        player_cards = " ".join(self.cog.get_emoji(card) for card in self.player_hand)
        dealer_cards = " ".join(self.cog.get_emoji(card) for card in self.dealer_hand)

        embed.add_field(name="Tus cartas", value=f"{player_cards} (Total: {self.player_total})")
        embed.add_field(name="Cartas del bot", value=f"{dealer_cards} (Total: {self.dealer_total})")

        if self.dealer_total > 21 or self.player_total > self.dealer_total:
            ganancia = self.amount * 0.2
            self.user_data['balance'] += ganancia
            self.bot_data['balance'] -= ganancia

            save_user_data(self.user_id, self.guild_id, self.user_data['balance'])
            save_user_data(self.bot_user_id, self.guild_id, self.bot_data['balance'])

            amount_format = f"${ganancia:,.0f}".replace(",", ".")
            balance_format = f"${self.user_data['balance']:,.0f}".replace(",", ".")
            embed.add_field(name="Resultado", value=f"¡Ganaste {amount_format}!\nTu nuevo saldo es {balance_format}", inline=False)
        elif self.player_total < self.dealer_total:
            self.user_data['balance'] -= self.amount
            self.bot_data['balance'] += self.amount

            save_user_data(self.user_id, self.guild_id, self.user_data['balance'])
            save_user_data(self.bot_user_id, self.guild_id, self.bot_data['balance'])

            amount_format = f"${self.amount:,.0f}".replace(",", ".")
            balance_format = f"${self.user_data['balance']:,.0f}".replace(",", ".")

            embed.add_field(name="Resultado", value=f"La casa gana. Perdiste {amount_format}. \nTu nuevo saldo es {balance_format}", inline=False)
        else:
            embed.add_field(name="Resultado", value="Es un empate.", inline=False)

        embed.set_thumbnail(url="https://pillan.inf.uct.cl/~fespinoza/images/blackjack.webp")
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    await bot.add_cog(Blackjack(bot))
