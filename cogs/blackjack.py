import discord
from discord.ext import commands
from discord.ui import Button, View
import random
from cogs.const.map import MAP_CARD, MAP_EMOJIS
from discord import app_commands


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
            total -= 10  # Adjust Ace value from 11 to 1
            ace_count -= 1
        return total

    def get_emoji(self, card):
        """Gets the emoji for a specific card based on its rank and suit."""
        return self.emoji_map.get(card, ":question:")

    @commands.command(name='blackjack', help='Comienza un juego de Blackjack contra el bot.')
    async def blackjack(self, ctx):
        await self._blackjack(ctx)

    @app_commands.command(name='blackjack', description='Comienza un juego de Blackjack contra el bot.')
    async def slash_blackjack(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._blackjack(ctx)

    async def _blackjack(self, ctx):
        """Start a game of Blackjack against the bot."""
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

        view = BlackjackView(player_hand, dealer_hand, player_total, dealer_total, self)
        await ctx.send(embed=embed, view=view)


class BlackjackView(View):
    def __init__(self, player_hand, dealer_hand, player_total, dealer_total, cog):
        super().__init__(timeout=60)
        self.player_hand = player_hand
        self.dealer_hand = dealer_hand
        self.player_total = player_total
        self.dealer_total = dealer_total
        self.cog = cog

    @discord.ui.button(label="Pedir", style=discord.ButtonStyle.primary)
    async def hit(self, interaction: discord.Interaction, button: Button):
        """Player requests another card."""
        new_card = self.cog.draw_card()
        self.player_hand.append(new_card)
        self.player_total = self.cog.calculate_total(self.player_hand)

        if self.player_total > 21:
            embed = discord.Embed(title="Blackjack", description="Te pasaste. Has perdido.", color=0xff0000)
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

        embed = discord.Embed(title="Blackjack", description="El juego ha terminado." if self.dealer_total > 21 else "El bot se planta.", color=0x00ff00)
        player_cards = " ".join(self.cog.get_emoji(card) for card in self.player_hand)
        dealer_cards = " ".join(self.cog.get_emoji(card) for card in self.dealer_hand)

        embed.add_field(name="Tus cartas", value=f"{player_cards} (Total: {self.player_total})")
        embed.add_field(name="Cartas del bot", value=f"{dealer_cards} (Total: {self.dealer_total})")

        if self.dealer_total > 21 or self.player_total > self.dealer_total:
            embed.add_field(name="Resultado", value="¡Ganaste!", inline=False)
        elif self.player_total < self.dealer_total:
            embed.add_field(name="Resultado", value="La casa gana.", inline=False)
        else:
            embed.add_field(name="Resultado", value="Es un empate.", inline=False)

        embed.set_thumbnail(url="https://pillan.inf.uct.cl/~fespinoza/images/blackjack.webp")
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot):
    await bot.add_cog(Blackjack(bot))
