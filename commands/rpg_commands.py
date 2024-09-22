import discord
from discord.ext import commands
from utils.rpg_data_manager import create_player, get_player_by_id, get_player_by_name, init_db, session,add_item_to_inventory, get_weapon_by_id, get_armor_by_id
from rpg_module.weapons import Weapon
from rpg_module.armors import Armor
import asyncio

# Inicializar la base de datos
init_db()

class StatAssignView(discord.ui.View):
    def __init__(self, player_stats):
        super().__init__()
        self.player_stats = player_stats

    async def update_embed(self, interaction):
        """Actualizar el embed después de que el usuario asigne puntos."""
        embed = discord.Embed(
            title=f"Asignación de puntos para {interaction.user.name}",
            description="Selecciona a qué atributo asignar tus puntos.",
            color=0x00ff00
        )
        embed.add_field(name="Puntos disponibles", value=self.player_stats.stats_points)
        embed.add_field(name="Fuerza", value=self.player_stats.strength)
        embed.add_field(name="Inteligencia", value=self.player_stats.intelligence)
        embed.add_field(name="Agilidad", value=self.player_stats.agility)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Fuerza +1", style=discord.ButtonStyle.primary)
    async def increase_strength(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player_stats.stats_points > 0:
            self.player_stats.strength += 1
            self.player_stats.stats_points -= 1
            session.commit()  # Guardar los cambios en la base de datos
            await self.update_embed(interaction)

    @discord.ui.button(label="Inteligencia +1", style=discord.ButtonStyle.primary)
    async def increase_intelligence(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player_stats.stats_points > 0:
            self.player_stats.intelligence += 1
            self.player_stats.stats_points -= 1
            session.commit()  # Guardar los cambios en la base de datos
            await self.update_embed(interaction)

    @discord.ui.button(label="Agilidad +1", style=discord.ButtonStyle.primary)
    async def increase_agility(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.player_stats.stats_points > 0:
            self.player_stats.agility += 1
            self.player_stats.stats_points -= 1
            session.commit()  # Guardar los cambios en la base de datos
            await self.update_embed(interaction)

class RPG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='Registra un jugador. Usa el comando solo una vez por usuario.')
    async def registerplayer(self, ctx):
        usuario = ctx.author
        user_id = str(usuario.id)

        # Verificar si el jugador ya está registrado
        player_data = get_player_by_id(user_id)
        if player_data:
            await ctx.send(f'{usuario.name}, ya estás registrado como jugador.')
            return

        # Registrar nuevo jugador con datos iniciales
        new_player = create_player(user_id)
        await ctx.send(f'{usuario.name}, has sido registrado como jugador con éxito.')

    @commands.command(help='Muestra las estadísticas de tu personaje.')
    async def stats(self, ctx):
        usuario = ctx.author
        user_id = str(usuario.id)

        # Cargar los datos del jugador
        player_data = get_player_by_id(user_id)
        if not player_data:
            await ctx.send(f'{usuario.name}, no estás registrado como jugador. Usa el comando !registerplayer para registrarte.')
            return

        # Crear el embed con las estadísticas
        embed = discord.Embed(
            title=f"Estadísticas de {usuario.name}",
            description="Aquí están tus estadísticas actuales:",
            color=0xFF5733
        )
        embed.add_field(name="Nivel", value=player_data.level)
        embed.add_field(name="Salud", value=player_data.health)
        embed.add_field(name="Mana", value=player_data.mana)
        embed.add_field(name="Fuerza", value=player_data.strength)
        embed.add_field(name="Inteligencia", value=player_data.intelligence)
        embed.add_field(name="Agilidad", value=player_data.agility)

        # Enviar el embed con las estadísticas
        await ctx.send(embed=embed)

    @commands.command(help="Asigna puntos de estadísticas.")
    async def assignstats(self, ctx):
        user_id = str(ctx.author.id)

        # Cargar los datos del jugador
        player_stats = get_player_by_id(user_id)
        if not player_stats:
            await ctx.send(f"{ctx.author.name}, no estás registrado como jugador.")
            return

        # Crear embed inicial con las estadísticas actuales
        embed = discord.Embed(
            title=f"Asignación de puntos para {ctx.author.name}",
            description="Selecciona a qué atributo asignar tus puntos.",
            color=0x00ff00
        )
        embed.add_field(name="Puntos disponibles", value=player_stats.stats_points)
        embed.add_field(name="Fuerza", value=player_stats.strength)
        embed.add_field(name="Inteligencia", value=player_stats.intelligence)
        embed.add_field(name="Agilidad", value=player_stats.agility)

        # Mostrar los botones y el embed
        view = StatAssignView(player_stats)
        await ctx.send(embed=embed, view=view)

    @commands.command(help="Muestra la tienda con los ítems disponibles.")
    async def list_shop(self, ctx):
        # Obtener todas las armas y armaduras
        weapons = session.query(Weapon).all()
        armors = session.query(Armor).all()

        items = weapons + armors
        items_per_page = 10
        pages = [items[i:i + items_per_page] for i in range(0, len(items), items_per_page)]

        embeds = []
        for i, page in enumerate(pages):
            embed = discord.Embed(title=f"Tienda de Ítems - Página {i + 1}/{len(pages)}", color=0x00ff00)
            for item in page:
                embed.add_field(name=f"{item.name} (ID: {item.id})", value=f"Daño: {getattr(item, 'base_damage', 'N/A')}, Defensa: {getattr(item, 'defense_value', 'N/A')}", inline=False)
            embeds.append(embed)

        message = await ctx.send(embed=embeds[0])

        if len(embeds) > 1:
            await self.paginate(ctx, message, embeds)

    async def paginate(self, ctx, message, embeds):
        current_page = 0

        await message.add_reaction("⬅️")
        await message.add_reaction("➡️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["⬅️", "➡️"] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "➡️":
                    if current_page < len(embeds) - 1:
                        current_page += 1
                        await message.edit(embed=embeds[current_page])
                elif str(reaction.emoji) == "⬅️":
                    if current_page > 0:
                        current_page -= 1
                        await message.edit(embed=embeds[current_page])

                await message.remove_reaction(reaction.emoji, user)

            except asyncio.TimeoutError:
                await message.clear_reactions()
                break
   

    @commands.command(help="Compra un ítem de la tienda usando su ID.")
    async def buy_item(self, ctx, item_id: int):
        player = get_player_by_name(str(ctx.author.id))
        if not player:
            await ctx.send("No estás registrado como jugador.")
            return

        # Buscar el ítem en las tablas de armas y armaduras
        item = get_weapon_by_id(item_id)
        item_type = 'weapon'
        if not item:
            item = get_armor_by_id(item_id)
            item_type = 'armor'

        if not item:
            await ctx.send("Ítem no encontrado.")
            return

        # Aquí deberías verificar si el jugador tiene suficiente dinero (Mellado Coins)
        # Si no tiene suficiente dinero, envía un mensaje de error y return.
        # ...

        # Añadir el ítem al inventario del jugador
        add_item_to_inventory(player.id, item_type, item.id)
        await ctx.send(f"Has comprado {item.name} y ha sido añadido a tu inventario.")

async def setup(bot):
    await bot.add_cog(RPG(bot))
