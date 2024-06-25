from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import logging
import random as ra
from discord import FFmpegPCMAudio
import yt_dlp as youtube_dl
import glob
from mutagen.mp3 import MP3
from a_queue.audio_queue import AudioQueue

handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   description="this is a bot the Caro", intents=intents)

audio_queue = AudioQueue()

# Ping-pong
@bot.command()
async def ping(ctx):
    await ctx.send('Un ingeniero duro programa todos los dias, si no no eres nadie.')

@bot.command()
async def best(ctx):
    await ctx.send('Mejor que un programador?, pues un ingeniero civil electrico, esos wns si son duro, sin ellos no habria nada de electricidad y ustedes saben los computadores viven de eso, 5vols 0 vols, 1 y 0 bits')

@bot.command()
async def duro(ctx):
    await ctx.send("Duro, duro, duro, duro, duro, duro, duro!!!!")

@bot.command()
async def mide(ctx):
    cm = ra.randint(1, 30)
    await ctx.send(f"Te mide: {cm} cm de puro placer bb 🍌")

@bot.command()
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

@bot.command()
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
        ·Luis Alberto Caro, Camilo Silva, Billy Peralta, Oriel A. Herrera, Sergio Barrientos – Real-Time Recognition of Arm motion Using Artificial Neural Network Multi-perceptron with Arduino One MicroController and EKG/EMG Shield Sensor.
        ·Luis Alberto Caro, Javier Correa, Pablo Espinace, Daniel Langdon, Daniel Maturana, Rubén Mitnik, Sebastian Montabone, Stefan Pszczólkowski, Anita Araneda, Domingo Mery, Miguel Torres, Alvaro Soto – Indoor Mobile Robotic at Grima, PUC.
        """, inline=True)
    embed.add_field(name="Áreas de Interés",
                    value="·Robótica Educativa, Sistemas Inteligentes, Internet de las Cosas + SmartCity.", inline=False)
    embed.set_footer(text="Lunes – Viernes: 9:00 – 15:00")
    embed.set_thumbnail(url="https://www.inf.uct.cl/wp-content/uploads/2018/10/Luis-Caro-577x1024.jpg")
    await ctx.send(embed=embed)

@bot.command()
async def interfaz(ctx):
    embed = discord.Embed()
    embed.title = "NO ME INTERESA LA INTERFACE"
    embed.description = "DEJAAA DE WEBEA CON LA INTERFAZ REQL, YO EVALUO LOS ALGORITMOS!!!!"
    embed.color = discord.Color.from_rgb(255,0,0)
    await ctx.send(embed=embed)

@bot.command()
async def pasa(ctx, user: discord.User):
    resultado = ra.randint(0, 1)
    if resultado == 1:
        await ctx.send(f"{user.mention} ¡Estás aprobado! 🎉")
    else:
        await ctx.send(f"{user.mention} Lamentablemente!, repruebas el ramo malo ql sin opción a repetir. 😢")

@bot.command()
async def aram(ctx):
    result = ra.randint(0,1)
    if result == 1:
        await ctx.send('@everyone ¡Hora de jugar ARAM! 🎮')
    else:
        await ctx.send('Hoy no se juega!')

@bot.command()
async def age(ctx):
    result = ra.randint(0,1)
    if result == 1:
        await ctx.send('@everyone ¡Hora de jugar su AGE 🥵🥵🥵')
    else:
        await ctx.send('En otro momento equisde')

@bot.command()
async def quesehace(ctx):
    await ctx.send('@everyone\nHoy solo se descansa gracias.')

@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("No estas conectado a ningun canal de voz")
        return
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command()
async def leave(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def play(ctx, filename: str, repeat: int = 1):
    if ctx.voice_client is None:
        await ctx.send("No estoy conectado a un canal de voz")
        return

    try:
        repeat = abs(int(repeat))
        if repeat < 1:
            raise ValueError
        repeat = min(repeat, 10)
    except (ValueError, SyntaxError, NameError):
        await ctx.send("ESCRIBE EL NUMERO BIEN SACO WEA")
        return

    directory = '/usr/home/users/fespinoza/bot_c/audio'
    file_path = glob.glob(os.path.join(directory, f"{filename}.*"))

    if not file_path:
        await ctx.send("El archivo especificado no existe.")
        return

    for _ in range(repeat):
        audio_queue.add(file_path[0])

    await ctx.send(f"Se ha agregado a la cola  {filename} repetido {repeat} veces")

    def play_next(_):
        if audio_queue.view_queue() and bot.is_playing_audio:
            next_audio = audio_queue.get_next_audio()
            ctx.send(f"Reproduciendo siguiente audio: {next_audio}")
            vc.play(FFmpegPCMAudio(next_audio), after=play_next)
    vc = ctx.voice_client
    bot.is_playing_audio = True

    if not vc.is_playing():
        next_audio = audio_queue.get_next_audio()
        await ctx.send(f"Reproduciendo audio inicial: {next_audio}")
        vc.play(FFmpegPCMAudio(next_audio), after=play_next)
    else:
        await ctx.send("Ya estoy reproduciendo audio.")

@bot.command()
async def add(ctx, filename: str):
    directory = '/usr/home/users/fespinoza/bot_c/audio'
    file_path = glob.glob(os.path.join(directory, f"{filename}.*"))

    if not file_path:
        await ctx.send("El archivo especificado no existe.")
        return

    audio_queue.add(filename)
    await ctx.send(f"Cola después de agregar '{filename}': {audio_queue.view_queue()}")

@bot.command()
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("No estoy conectado a un canal de voz")
        return

    if ctx.voice_client.is_playing():
        bot.is_playing_audio = False
        ctx.voice_client.stop()
        await ctx.send(f"Reproducción detenida. Cola actual: {audio_queue.view_queue()}")
    else:
        await ctx.send("No estoy reproduciendo ningún audio.")

@bot.command()
async def q(ctx):
    if audio_queue.view_queue():
        queue_list = audio_queue.view_queue()
        queue_str = '\n'.join([f"{idx + 1}. {os.path.basename(audio)}" for idx, audio in enumerate(queue_list)])
        embed = discord.Embed(title="Cola de Reproducción", color=discord.Color.blurple())
        embed.description = queue_str
        await ctx.send(embed=embed)
    else:
        await ctx.send("La cola está vacía.")

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Audio saltado. Cola actual:", audio_queue.view_queue())
    else:
        await ctx.send("No estoy reproduciendo ningún audio.")

@bot.command()
async def remove(ctx, index: int):
    try:
        audio_queue.remove_audio(index - 1)
        await ctx.send(f"Audio en la posición {index} eliminado. Cola actual:", audio_queue.view_queue())
    except IndexError:
        await ctx.send("Índice fuera de rango al intentar eliminar audio. Cola actual:", audio_queue.view_queue())

@bot.command()
async def list(ctx):
    directory = '/usr/home/users/fespinoza/bot_c/audio'
    embed = discord.Embed(
        title="Lista de reproducción disponible",
        url="https://media.licdn.com/dms/image/C5603AQHFwyRGQtuSUA/profile-displayphoto-shrink_200_200/0/1516997163523?e=2147483647&v=beta&t=WtAtj17uSKfW4cIb1Ki8o4fBeqXTOnR4qooq9wSb8zI",
        description="Uso: !play fileName",
        color=0xFF5733
    )
    embed.set_author(
        name="Dr(c) Luis Alberto Caro",
        url="https://media.licdn.com/dms/image/C5603AQHFwyRGQtuSUA/profile-displayphoto-shrink_200_200/0/1516997163523?e=2147483647&v=beta&t=WtAtj17uSKfW4cIb1Ki8o4fBeqXTOnR4qooq9wSb8zI"
    )

    if not os.path.exists(directory):
        await ctx.send("El directorio especificado no existe.")
        return

    files = os.listdir(directory)

    if not files:
        await ctx.send("El directorio está vacío.")
        return

    i = 1
    for file in files:
        file_path = os.path.join(directory, file)
        if file.endswith('.mp3'):
            audio = MP3(file_path)
            duration = int(audio.info.length)
            minutes, seconds = divmod(duration, 60)
            duration_str = f"{minutes}:{seconds:02d}"
            file_name = file.split('.')[0]
            embed.add_field(name="", value=f'{i}. {file_name} - ({duration_str})', inline=True)
            i += 1

    embed.set_footer(text="Lunes – Viernes: 6:00 – ??:??")
    embed.set_thumbnail(url="https://media.licdn.com/dms/image/C5603AQHFwyRGQtuSUA/profile-displayphoto-shrink_200_200/0/1516997163523?e=2147483647&v=beta&t=WtAtj17uSKfW4cIb1Ki8o4fBeqXTOnR4qooq9wSb8zI")
    await ctx.send(embed=embed)

@bot.command()
async def hello(ctx):
    embed = discord.Embed()
    embed.title = "Hola mis queridos estudiantes,"
    embed.description = "los invito a estudiar un entretenido curso de Pascal, un potententisimo lenguaje de programación: [CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT](https://www.youtube.com/watch?v=yvFCI2whgOA)."
    embed.color = embed.color = discord.Color.from_rgb(251, 141, 25)
    embed.set_thumbnail(
        url="https://jomerlisriera.files.wordpress.com/2015/03/lazarus_logo_new.png")
    await ctx.send(embed=embed)

@bot.command()
async def diuca(ctx):
    await ctx.send("ESTOY CANSADO JEFE\nSaquenme de acªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªªª")
    await ctx.send("https://pillan.inf.uct.cl/~fespinoza/file.jpg")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='[CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT]'), status=discord.Status.dnd)
    print(f'We have logged in as {bot.user}')

bot.run(token, log_handler=handler)
