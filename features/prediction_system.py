import discord
from discord.ext import commands
from discord.ui import Button, View
from utils.prediction_manager import *
from datetime import datetime


import re
from datetime import datetime


import re
from datetime import datetime


class Prediction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="prediccion")
    async def create_prediction(self, ctx, *, args: str):
        # Separar la pregunta y la fecha
        try:
            pregunta, fecha = args.rsplit(' ', 1)
        except ValueError:
            await ctx.send("Formato incorrecto. Usa: !prediccion <pregunta> <fecha>")
            return

        # Validar la fecha con expresión regular que permita uno o dos dígitos
        date_pattern = re.compile(r'^\d{1,2}/\d{1,2}$')
        if not date_pattern.match(fecha):
            await ctx.send("Formato de fecha incorrecto. Usa el formato DD/MM.")
            return

        # Obtener la fecha actual para determinar el año
        today = datetime.now()

        # Dividir la fecha ingresada
        day, month = map(int, fecha.split('/'))

        # Determinar el año
        if month < today.month or (month == today.month and day < today.day):
            year = today.year + 1
        else:
            year = today.year

        # Convertir la fecha a formato datetime
        try:
            fecha_limite = datetime(year, month, day)
        except ValueError:
            await ctx.send("Fecha no válida.")
            return

        # Guardar la predicción en la base de datos
        prediction_id = create_prediction(
            pregunta, fecha_limite, ctx.author.id)

        # Crear vista para votar
        view = VoteView(prediction_id)
        await ctx.send(f"Predicción creada: {pregunta}\n¡Comienza la votación!", view=view)

    @commands.command(name="predicciones")
    async def list_predictions(self, ctx):
        predictions = get_all_predictions()
        if not predictions:
            await ctx.send("No hay predicciones activas.")
            return

        embed = discord.Embed(
            title="Predicciones Actuales",
            description="Aquí están las predicciones activas junto con sus resultados.",
            color=discord.Color.blue(),  # Puedes cambiar el color aquí
            timestamp=ctx.message.created_at
        )

        for pred in predictions:
            embed.add_field(
                name=f"Pregunta: {pred['pregunta']}",
                value=f"Fecha límite: {pred['fecha_limite'].strftime(
                    '%d/%m/%Y')}\nVotos SI: {pred['votos_si']} | Votos NO: {pred['votos_no']}",
                inline=False
            )

        embed.set_footer(text=f"Solicitado por {
                         ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)


class VoteView(View):
    def __init__(self, prediction_id):
        super().__init__()
        self.prediction_id = prediction_id

    @discord.ui.button(label="SI", style=discord.ButtonStyle.green)
    async def vote_yes(self, interaction: discord.Interaction, button: Button):
        result = cast_vote(interaction.user.id, self.prediction_id, "si")
        if result:
            await interaction.response.send_message("Has votado SI.", ephemeral=True)
        else:
            await interaction.response.send_message("Ya has votado o hubo un error.", ephemeral=True)

    @discord.ui.button(label="NO", style=discord.ButtonStyle.red)
    async def vote_no(self, interaction: discord.Interaction, button: Button):
        result = cast_vote(interaction.user.id, self.prediction_id, "no")
        if result:
            await interaction.response.send_message("Has votado NO.", ephemeral=True)
        else:
            await interaction.response.send_message("Ya has votado o hubo un error.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Prediction(bot))
