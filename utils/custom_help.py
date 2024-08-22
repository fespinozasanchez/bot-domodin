import discord
from discord.ext import commands
from discord.ui import View, Button


class CustomHelpPaginator(View):
    def __init__(self, embeds):
        super().__init__(timeout=None)
        self.embeds = embeds
        self.current_page = 0

        # Deshabilita los botones iniciales en la primera página
        self.first_page.disabled = True
        self.previous_page.disabled = True

    async def update_buttons(self, interaction):
        self.first_page.disabled = self.current_page == 0
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == len(self.embeds) - 1
        self.last_page.disabled = self.current_page == len(self.embeds) - 1
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label='⏮️', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = 0
        await self.update_buttons(interaction)

    @discord.ui.button(label='◀️', style=discord.ButtonStyle.blurple)
    async def previous_page(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_buttons(interaction)

    @discord.ui.button(label='▶️', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await self.update_buttons(interaction)

    @discord.ui.button(label='⏭️', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: Button):
        self.current_page = len(self.embeds) - 1
        await self.update_buttons(interaction)


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embeds = []
        embed = discord.Embed(
            title="Comandos del Bot",
            description="Aquí tienes una lista de todos los comandos disponibles organizados por categorías.",
            color=discord.Color.blue()
        )

        # Recorrer cada "Cog" y sus comandos
        for cog, commands in mapping.items():
            command_signatures = [
                self.get_command_signature(c) for c in commands]

            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Sin categoría")

                # Dividir comandos en dos columnas
                half = len(command_signatures) // 2 + \
                    (len(command_signatures) % 2)
                column1 = command_signatures[:half]
                column2 = command_signatures[half:]

                # Agregar las dos columnas al embed, con formato más limpio
                embed.add_field(name=f"{
                                cog_name} (1/2)", value="\n".join(column1) or "No hay comandos.", inline=True)
                embed.add_field(name=f"{
                                cog_name} (2/2)", value="\n".join(column2) or "No hay comandos.", inline=True)

                # Limitar los campos por embed para evitar overflow
                if len(embed.fields) >= 6:
                    embeds.append(embed)
                    embed = discord.Embed(
                        title="Comandos del Bot",
                        color=discord.Color.blue()
                    )

        if embed.fields:
            embeds.append(embed)

        if embeds:
            view = CustomHelpPaginator(embeds)
            await self.get_destination().send(embed=embeds[0], view=view)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"Comandos en {cog.qualified_name}",
            description=cog.description or "No hay descripción disponible.",
            color=discord.Color.blue()
        )
        commands = cog.get_commands()
        for command in commands:
            embed.add_field(
                name=self.get_command_signature(command),
                value=command.help or "No hay descripción disponible.",
                inline=False
            )
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=self.get_command_signature(group),
            description=group.help or "No hay descripción disponible.",
            color=discord.Color.blue()
        )
        subcommands = group.commands
        for command in subcommands:
            embed.add_field(
                name=self.get_command_signature(command),
                value=command.help or "No hay descripción disponible.",
                inline=False
            )
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=self.get_command_signature(command),
            description=command.help or "No hay descripción disponible.",
            color=discord.Color.blue()
        )
        await self.get_destination().send(embed=embed)
