import random as ra
import discord
from discord.ext import commands,tasks
from commands.CONST.payas import PAYAS
from PIL import Image
from datetime import datetime

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

    @bot.command(help="Documentación del PIC 12F629")
    async def ref(ctx):
        embed = discord.Embed()
        embed.title = "Mis queridos Alumnos"
        embed.set_author(name="Dr(c) Luis Alberto Caro", url="https://www.inf.uct.cl/luis-caro/",
                         icon_url="https://www.inf.uct.cl/wp-content/uploads/2018/10/Luis-Caro-577x1024.jpg")
        embed.description = "Les invito a leer este potentisimo documento, para que puedan desenvolverse con una gran facilidad en nuestro maravilloso micro-controlador PIC 12F629 [PIC 12F629](https://ww1.microchip.com/downloads/en/devicedoc/41190c.pdf)."
        embed.color = discord.Color.from_rgb(241, 0, 232)
        embed.set_thumbnail(
            url="https://www.microchip.com/content/dam/mchp/mrt-dam/ic-images/dfn-s/8-lead-a6x/PIC12F629-A6X-FlipFlop2.jpg")
        embed.set_footer(text="Information requested by: {}".format(
            ctx.author.display_name))
        await ctx.send(embed=embed)

    @bot.command(help="Información del Dr(c) Luis Alberto Caro")
    async def info(ctx):
        embed = discord.Embed(title="Ingeniero Civil Informático", url="https://www.inf.uct.cl/wp-content/uploads/2018/10/Luis-Caro-577x1024.jpg",
                              description="Dr.(c). en Ciencias de la Ingeniería, área Ciencia de la Computación.", color=0xFF5733)
        embed.set_author(name="Dr(c) Luis Alberto Caro", url="https://www.inf.uct.cl/luis-caro/",
                         icon_url="https://www.inf.uct.cl/wp-content/uploads/2018/10/Luis-Caro-577x1024.jpg")
        embed.add_field(name="Áreas Generales de Investigación",
                        value="·Robótica Educativa\n·Sistemas Inteligentes\n·Internet de las Cosas + SmartCity", inline=True)
        embed.add_field(name="Áreas de Docencia",
                        value="·Programación II.\n·Programación Integración de Sistemas.\n·Arquitectura de Hardware.\n·Micro Controladores.\n·Interfaces Gráficas.", inline=True)
        embed.add_field(name="Otros Antecedentes", value="·Director del Centro de Desarrollo de Software y Tecnología – CEDEST.\n·Docente del plan especial de ingeniería informática para técnicos.\n·Profesor programa de Magister de Matemáticas de Universidad Católica de Temuco.\n·Expositor permanente de Casa Abierta y vínculo con colegios y liceos de la zona.\n·Coordinador responsable evento OCI-2018", inline=False)
        embed.add_field(name="Publicaciones", value="""
            ·Billy Peralta, Luis Alberto Caro , Alvaro Soto – Unsupervised Local Regressive Attributes for Pedestrian Re-Identification.
            ·Billy Peralta, Ariel Saavedra, Luis Alberto Caro – A proposal for mixture of experts with entropic regularization.
            ·Billy Peralta, Luis Alberto Caro – Improved Object Recognition with Decision Trees Using Subspace Clustering.
            ·Billy Peralta, Luis Alberto Caro, Alvaro Soto – A proposal for supervised clustering with Dirichlet Process using labels.
            ·Billy Peralta, L. Parra, Luis Alberto Caro – Evaluation of stacked auto-encoders for pedestrian detection.
            """, inline=True)
        embed.add_field(name="Publicaciones", value="""
            ·Billy Peralta, T. Poblete, Luis Alberto Caro – Automatic feature selection for desertion and graduation prediction: A Chilean case.
            ·Luis Alberto Caro, Camilo Silva, Billy Peralta, Oriel A. Herrera, Sergio Barrientos – Real-Time Recognition of Arm motion Using Artificial Neural Network Multi-perceptron with Arduino One MicroController y EKG/EMG Shield Sensor.
            ·Luis Alberto Caro, Javier Correa, Pablo Espinace, Daniel Langdon, Daniel Maturana, Rubén Mitnik, Sebastian Montabone, Stefan Pszczólkowski, Anita Araneda, Domingo Mery, Miguel Torres, Alvaro Soto – Indoor Mobile Robotic at Grima, PUC.
            """, inline=True)
        embed.add_field(name="Áreas de Interés",
                        value="·Robótica Educativa, Sistemas Inteligentes, Internet de las Cosas + SmartCity.", inline=False)
        embed.set_footer(text="Lunes – Viernes: 9:00 – 15:00")
        embed.set_thumbnail(
            url="https://www.inf.uct.cl/wp-content/uploads/2018/10/Luis-Caro-577x1024.jpg")
        await ctx.send(embed=embed)

    # Fecha límite
    fecha_inicio = datetime(2024, 9, 4)
    fecha_limite = datetime(2024, 9, 18)

    # Ruta de la imagen
    imagen_mario = "commands\img\mario18.jpg"

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
            imagen_mario = Image.open("commands\img\mario18.jpg")  # Asegúrate de usar la ruta correcta
            imagen = ajustar_opacidad(imagen_mario, opacidad)
            imagen.save("mario_opacidad.png")

            # Enviar imagen ajustada con opacidad
            await ctx.send(
                f"{usuario.mention}, tu disponibilidad es del {porcentaje_disponibilidad * 100:.2f}% ({dias_restantes} días restantes).",
                file=discord.File("mario_opacidad.png")
            )
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




