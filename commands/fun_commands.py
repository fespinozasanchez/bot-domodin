import random as ra
import discord
from discord.ext import commands, tasks
from commands.CONST.payas import PAYAS
from PIL import Image
from datetime import datetime
from pathlib import Path


def register_commands(bot):
    @bot.command(help="¿Qué es un ingeniero?")
    async def ping(ctx):
        await ctx.send('Un ingeniero duro programa todos los dias, si no no eres nadie.')

    @bot.command(help="¿Quién es el mejor programador?")
    async def best(ctx):
        await ctx.send('Mejor que un programador?, pues un ingeniero civil electrico, esos wns si son duro, sin ellos no habria nada de electricidad y ustedes saben los computadores viven de eso, 5vols 0 vols, 1 y 0 bits')

    @bot.command(help="Duro, duro, duro, duro, duro, duro, duro!!!!")
    async def duro(ctx):
        await ctx.send("Duro, duro, duro, duro, duro, duro, duro!!!!")

    @bot.command(help="Mide tu pene")
    async def mide(ctx):
        cm = ra.randint(1, 30)
        await ctx.send(f"Te mide: {cm} cm de puro placer bb 🍌 {ctx.author.mention}")

    @bot.command(help="Payas")
    async def payas(ctx):
        await ctx.send(ra.choice(PAYAS))

    @bot.command(help="Manda a dormir a la gente")
    async def tutito(ctx):
        choice = ra.randint(0, 1)
        if choice == 1:
            await ctx.send(f"Anda a acostarte mierda! {ctx.author.mention}")
        else:
            await ctx.send(f"Los ingenieros duros no duermen {ctx.author.mention}")

    @bot.command(help="Pregunta si pasa el ramo")
    async def pasa(ctx, user: discord.User):
        resultado = ra.randint(0, 1)
        if resultado == 1:
            await ctx.send(f"{user.mention} ¡Estás aprobado! 🎉")
        else:
            await ctx.send(f"{user.mention} Lamentablemente!, repruebas el ramo malo ql sin opción a repetir. 😢")

    @bot.command(help="Prendio la Luchoneta")
    async def luchoneta(ctx):
        await ctx.send(f"@everyone MAMI PRENDA LA RADIO ENCIENDA LA TELE Y NO ME MOLESTE QUE HOY JUEGA LA LUCHONETA 🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️🗣️💥💥💥💥💥‼️‼️‼️❗❗❗❗⁉️")

    @bot.command()
    async def stream(ctx):
        # Crear el embed con la información del stream
        embed = discord.Embed(
            title="2 dias stremeando seguido? en mi prime jugando soloq mañanero en el gran high elo de bronce las !ig !only !barbería !donacion",
            description="Mira la transmisión en Twitch",
            url="https://www.twitch.tv/wenaluis",
            color=discord.Color.purple()
        )

        # Agregar una imagen (generalmente un avatar o banner del stream)
        embed.set_thumbnail(url="https://static-cdn.jtvnw.net/jtv_user_pictures/3adc7ba56988787b-profile_image-70x70.jpeg")  # Reemplaza con la URL de la imagen del stream

        # Agregar un campo con el nombre del canal
        embed.add_field(name="Canal:", value="wenaluis", inline=False)

        # Agregar un campo con el enlace directo al stream
        embed.add_field(name="Enlace:", value="[Ver el stream](https://www.twitch.tv/wenaluis)", inline=False)

        # Enviar el embed en el canal
        await ctx.send(embed=embed)

    @bot.command(help="Pregunta por una partida de age")
    async def age(ctx):
        choice = ra.randint(0, 1)
        if choice == 1:
            await ctx.send(f"@everyone Hora de jugar AGE 🥵🥵🥵🥵🥵")
        if choice == 0:
            await ctx.send(f"Hoy dia no toca")

    @bot.command(name="amongus", help="Pregunta por una partida de Amongus")
    async def amongus(ctx):
        choice = ra.randint(0, 1)
        if choice == 1:
            await ctx.send(f"@everyone Hora de jugar Among US 🥵🥵🥵🥵🥵 \n<a:amongus:1282901401369841664>")
        if choice == 0:
            await ctx.send(f"Hoy dia no toca \n<a:amongus:1282901401369841664>")

    @bot.command(name="domodin", help="dueño de domodin esta vigilando")
    async def domodin(ctx):
        await ctx.send(f"<:domodin:1282771742154162226>")

    @bot.command(help="Pregunta que se hace hoy")
    async def quesehace(ctx):
        await ctx.send('@everyone\nHoy solo se descansa gracias.')

    @bot.command(help="Pregunta por una partida de aram")
    async def aram(ctx):
        result = ra.randint(0, 1)
        if result == 1:
            await ctx.send('@everyone ¡Hora de jugar ARAM! 🎮')
            await ctx.send("https://i.imgflip.com/7mwjwz.png?a477192")
        else:
            await ctx.send('Hoy no se juega!')

    # Fecha límite
    fecha_inicio = datetime(2024, 9, 4)
    fecha_limite = datetime(2024, 9, 18)

    # Ruta de la imagen (usamos pathlib para garantizar compatibilidad multiplataforma)
    imagen_mario_path = Path("commands/img/mario18.jpg")

    # Función para ajustar la opacidad de una imagen
    def ajustar_opacidad(imagen, opacidad):
        imagen = imagen.convert("RGBA")
        alpha = imagen.split()[3]  # Obtiene el canal alpha (opacidad)
        alpha = alpha.point(lambda p: p * opacidad)  # Ajusta la opacidad
        imagen.putalpha(alpha)
        return imagen

    @bot.command(name="mario")
    async def mario(ctx):
        usuario = await bot.fetch_user(429798122768564225)  # ID de Mario
        hoy = datetime.now()

        # Si estamos dentro del rango de fechas
        if fecha_inicio <= hoy <= fecha_limite:
            # Calcular el total de días y los días restantes
            dias_totales = (fecha_limite - fecha_inicio).days
            dias_restantes = (fecha_limite - hoy).days

            # Calcular el porcentaje de disponibilidad
            porcentaje_disponibilidad = dias_restantes / dias_totales

            # Ajustar la opacidad de la imagen según el porcentaje de disponibilidad
            opacidad = porcentaje_disponibilidad  # Opacidad entre 0.0 y 1.0

            # Cargar la imagen
            if imagen_mario_path.exists():
                imagen_mario = Image.open(imagen_mario_path)  # Usamos la ruta correcta multiplataforma
                imagen = ajustar_opacidad(imagen_mario, opacidad)
                imagen.save("mario_opacidad.png")

                # Enviar imagen ajustada con opacidad
                await ctx.send(
                    f"{usuario.mention}, tu disponibilidad es del {porcentaje_disponibilidad * 100:.2f}% ({dias_restantes} días restantes).",
                    file=discord.File("mario_opacidad.png")
                )
            else:
                await ctx.send("No se pudo encontrar la imagen especificada.")
        elif hoy < fecha_inicio:
            # Si la fecha actual es anterior al inicio de la cuenta regresiva
            await ctx.send(f"{usuario.mention}, tu disponibilidad aún no ha comenzado.")
        else:
            # Cuando llega la fecha límite o pasa
            await ctx.send(f"{usuario.mention}, tu disponibilidad ha llegado a 0. No queda tiempo.")

    @tasks.loop(hours=24)
    async def verificar_opacidad():
        canal = bot.get_channel(1234567890)  # Reemplaza con el ID de tu canal
        dias_restantes = (fecha_limite - datetime.now()).days

        if dias_restantes <= 0:
            await canal.send("Disponibilidad de Mario: 0")
            verificar_opacidad.cancel()

    @verificar_opacidad.before_loop
    async def before_verificar_opacidad():
        await bot.wait_until_ready()

    @bot.event
    async def on_ready():
        if not verificar_opacidad.is_running():
            verificar_opacidad.start()
        print(f'Bot {bot.user} ha iniciado.')
