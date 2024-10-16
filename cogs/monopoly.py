import discord
from discord.ext import commands, tasks
from discord.ui import View, Button, Select
import random as ra
import logging

class Monopoly(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jugadores = {}

    # Comando para mostrar una interfaz visual similar a un mapa de Monopoly
    @commands.command(name='monopoly')
    async def monopoly(self, ctx):
        # Creamos un botón para unirse al juego
        join_button = Button(label="Unirse al juego", style=discord.ButtonStyle.success)

        async def join_callback(interaction):
            jugador = interaction.user.name
            if jugador not in self.jugadores:
                self.jugadores[jugador] = 0  # Todos los jugadores empiezan en la casilla de inicio (posición 0)
                await interaction.response.send_message(f"{jugador} se ha unido al juego!", ephemeral=True)
            else:
                await interaction.response.send_message(f"{jugador}, ya estás en el juego!", ephemeral=True)

        # Asignamos la función callback al botón de unirse
        join_button.callback = join_callback

        # Creamos un botón para mover al jugador
        move_button = Button(label="Mover", style=discord.ButtonStyle.primary)

        async def move_callback(interaction):
            jugador = interaction.user.name
            if jugador in self.jugadores:
                movimiento = ra.randint(1, 6)  # Tirar un dado para mover de 1 a 6 casillas
                self.jugadores[jugador] = (self.jugadores[jugador] + movimiento) % 6  # Actualizamos la posición del jugador
                await interaction.response.send_message(f"{jugador} ha avanzado {movimiento} casillas y ahora está en la casilla {self.jugadores[jugador]}", ephemeral=True)
            else:
                await interaction.response.send_message(f"{jugador}, necesitas unirte al juego primero!", ephemeral=True)

        # Asignamos la función callback al botón de mover
        move_button.callback = move_callback

        # Creamos una representación visual del tablero de Monopoly con casillas
        tablero = "\n".join([
            "Inicio [ 👤 " + ", 👤 ".join([jugador for jugador, posicion in self.jugadores.items() if posicion == 0]) + " ]" if any(posicion == 0 for posicion in self.jugadores.values()) else "Inicio [ ]",
            "Casilla 1 [ 👤 " + ", 👤 ".join([jugador for jugador, posicion in self.jugadores.items() if posicion == 1]) + " ]" if any(posicion == 1 for posicion in self.jugadores.values()) else "Casilla 1 [ ]",
            "Casilla 2 [ 👤 " + ", 👤 ".join([jugador for jugador, posicion in self.jugadores.items() if posicion == 2]) + " ]" if any(posicion == 2 for posicion in self.jugadores.values()) else "Casilla 2 [ ]",
            "Casilla 3 [ 👤 " + ", 👤 ".join([jugador for jugador, posicion in self.jugadores.items() if posicion == 3]) + " ]" if any(posicion == 3 for posicion in self.jugadores.values()) else "Casilla 3 [ ]",
            "Casilla 4 [ 👤 " + ", 👤 ".join([jugador for jugador, posicion in self.jugadores.items() if posicion == 4]) + " ]" if any(posicion == 4 for posicion in self.jugadores.values()) else "Casilla 4 [ ]",
            "Casilla 5 [ 👤 " + ", 👤 ".join([jugador for jugador, posicion in self.jugadores.items() if posicion == 5]) + " ]" if any(posicion == 5 for posicion in self.jugadores.values()) else "Casilla 5 [ ]",
        ])

        # Creamos una vista que contendrá los botones de unirse y mover
        view = View()
        view.add_item(join_button)
        view.add_item(move_button)

        # Enviamos el mensaje con el tablero y la vista
        await ctx.send(f"Tablero de Monopoly:\n{tablero}", view=view)

async def setup(bot):
    await bot.add_cog(Monopoly(bot))
