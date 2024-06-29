import discord
from discord.ext import commands
from datetime import datetime, timedelta


def register_commands(bot, reminder_manager):
    @bot.command(help="Establece un recordatorio para una hora específica. Usa el formato HH:MM.")
    async def recordar(ctx, time: str, *, message: str):
        try:
            reminder_time = datetime.strptime(time, '%H:%M').time()
            now = datetime.now()
            reminder_datetime = datetime.combine(now, reminder_time)

            if reminder_datetime < now:
                reminder_datetime += timedelta(days=1)

            reminder_manager.add_reminder(
                reminder_datetime, message, ctx.channel.id)
            await ctx.send(f"Recordatorio establecido para las {time} con el mensaje: {message}")
        except ValueError:
            await ctx.send("Formato de hora no válido. Usa HH:MM en formato 24 horas.")

    @bot.command(help="Muestra una lista de todos los recordatorios establecidos.")
    async def recordatorios(ctx):
        reminders = reminder_manager.get_reminders()
        if reminders:
            embed = discord.Embed(title="Recordatorios",
                                  color=discord.Color.blurple())
            for idx, (reminder_time, message, channel_id) in enumerate(reminders):
                embed.add_field(name=f"Recordatorio {idx + 1}", value=f"Hora: {
                                reminder_time.strftime('%H:%M')} - Mensaje: {message}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("No hay recordatorios establecidos.")

    @bot.command(help="Elimina un recordatorio por su índice.")
    async def remover_recordatorio(ctx, index: int):
        reminder = reminder_manager.remove_reminder(index - 1)
        if reminder:
            await ctx.send(f"Recordatorio para las {reminder[0].strftime('%H:%M')} con el mensaje: {reminder[1]} ha sido eliminado.")
        else:
            await ctx.send("Índice fuera de rango. Por favor, proporciona un índice válido.")
