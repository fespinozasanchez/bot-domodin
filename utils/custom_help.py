import discord
from discord.ext import commands


class CustomHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="Comandos del Bot",
            description="Aquí tienes una lista de todos los comandos disponibles.",
            color=discord.Color.blue()
        )

        for cog, commands in mapping.items():
            command_signatures = [
                self.get_command_signature(c) for c in commands]
            if command_signatures:
                cog_name = getattr(cog, "qualified_name", "Sin categoría")
                # Dividir los comandos en grupos para columnas
                columns = [command_signatures[i:i + 5]
                           for i in range(0, len(command_signatures), 5)]
                for column in columns:
                    embed.add_field(
                        name=cog_name,
                        value="\n".join(column),
                        inline=True
                    )

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
            title=f"Comandos en {cog.qualified_name}",
            description=cog.description,
            color=discord.Color.blue()
        )
        commands = cog.get_commands()
        for command in commands:
            embed.add_field(
                name=self.get_command_signature(command),
                value=command.help or "No hay descripción disponible",
                inline=False
            )
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
            title=self.get_command_signature(group),
            description=group.help or "No hay descripción disponible",
            color=discord.Color.blue()
        )
        subcommands = group.commands
        for command in subcommands:
            embed.add_field(
                name=self.get_command_signature(command),
                value=command.help or "No hay descripción disponible",
                inline=False
            )
        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
            title=self.get_command_signature(command),
            description=command.help or "No hay descripción disponible",
            color=discord.Color.blue()
        )
        channel = self.get_destination()
        await channel.send(embed=embed)
