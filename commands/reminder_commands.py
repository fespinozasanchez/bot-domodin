import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.reminder_manager import ReminderManager


class Reminder(commands.Cog):
    def __init__(self, bot, reminder_manager: ReminderManager):
        self.bot = bot
        self.reminder_manager = reminder_manager

    @commands.command(help="Establece un recordatorio para una fecha y hora específicas. Usa el formato DD/MM/YYYY HH:MM.")
    async def recordar(self, ctx, datetime_str: str, *, message: str):
        try:
            # Intentamos convertir la entrada a un objeto datetime
            reminder_datetime = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M')
            now = datetime.now()

            if reminder_datetime < now:
                await ctx.send("La fecha y hora proporcionadas ya han pasado. Por favor, proporciona una fecha futura.")
                return

            # Guardamos el recordatorio
            self.reminder_manager.add_reminder(
                reminder_datetime, message, ctx.channel.id)
            await ctx.send(f"Recordatorio establecido para {reminder_datetime.strftime('%d/%m/%Y %H:%M')} con el mensaje: {message}")
        except ValueError:
            await ctx.send("Formato no válido. Usa DD/MM/YYYY HH:MM en formato 24 horas.")

    @commands.command(help="Muestra una lista de todos los recordatorios establecidos.")
    async def recordatorios(self, ctx):
        reminders = self.reminder_manager.get_reminders()
        if reminders:
            embed = discord.Embed(title="Recordatorios",
                                  color=discord.Color.blurple())
            for reminder in reminders:
                # Mostrar la fecha y hora del recordatorio
                embed.add_field(name=f"Recordatorio {reminder['id']}",
                                value=f"Fecha y hora: {reminder['reminder_time'].strftime('%d/%m/%Y %H:%M')} - Mensaje: {reminder['message']}",
                                inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No hay recordatorios establecidos.")

    @commands.command(help="Elimina un recordatorio por su índice.")
    async def remover_recordatorio(self, ctx, reminder_id: int):
        reminder = self.reminder_manager.remove_reminder(reminder_id)
        if reminder:
            await ctx.send(f"Recordatorio para {reminder['reminder_time'].strftime('%d/%m/%Y %H:%M')} con el mensaje: {reminder['message']} ha sido eliminado.")
        else:
            await ctx.send("Índice fuera de rango. Por favor, proporciona un índice válido.")


async def setup(bot):
    reminder_manager = ReminderManager()
    await bot.add_cog(Reminder(bot, reminder_manager))
