import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.reminder_manager import ReminderManager


class Reminder(commands.Cog):
    def __init__(self, bot, reminder_manager: ReminderManager):
        self.bot = bot
        self.reminder_manager = reminder_manager

    @commands.command(help="Establece un recordatorio para una hora específica. Usa el formato HH:MM.")
    async def recordar(self, ctx, time: str, *, message: str):
        try:
            reminder_time = datetime.strptime(time, '%H:%M').time()
            now = datetime.now()
            reminder_datetime = datetime.combine(now, reminder_time)

            if reminder_datetime < now:
                reminder_datetime += timedelta(days=1)

            self.reminder_manager.add_reminder(
                reminder_datetime, message, ctx.channel.id)
            await ctx.send(f"Recordatorio establecido para las {time} con el mensaje: {message}")
        except ValueError:
            await ctx.send("Formato de hora no válido. Usa HH:MM en formato 24 horas.")

    @commands.command(help="Muestra una lista de todos los recordatorios establecidos.")
    async def recordatorios(self, ctx):
        reminders = self.reminder_manager.get_reminders()
        if reminders:
            embed = discord.Embed(title="Recordatorios",
                                  color=discord.Color.blurple())
            for reminder in reminders:
                embed.add_field(
                    name=f"Recordatorio {reminder['id']}",
                    value=f"Hora: {reminder['reminder_time'].strftime(
                        '%H:%M')} - Mensaje: {reminder['message']}",
                    inline=False
                )
            await ctx.send(embed=embed)
        else:
            await ctx.send("No hay recordatorios establecidos.")

    @commands.command(help="Elimina un recordatorio por su índice.")
    async def remover_recordatorio(self, ctx, reminder_id: int):
        reminder = self.reminder_manager.remove_reminder(reminder_id)
        if reminder:
            await ctx.send(f"Recordatorio para las {reminder['reminder_time'].strftime('%H:%M')} con el mensaje: {reminder['message']} ha sido eliminado.")
        else:
            await ctx.send("Índice fuera de rango. Por favor, proporciona un índice válido.")


async def setup(bot):
    reminder_manager = ReminderManager()
    await bot.add_cog(Reminder(bot, reminder_manager))
