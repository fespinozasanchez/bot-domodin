from dotenv import load_dotenv
import discord
from discord.ext import commands
import os
import logging
import random as ra


handler = logging.FileHandler(
    filename='logs/discord.log', encoding='utf-8', mode='w')


load_dotenv()
token = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!',
                   description="this is a bot the Caro", intents=intents)


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


# Hello
@bot.command()
async def hello(ctx):
    embed = discord.Embed()
    embed.title = "Hola mis queridos estudiantes,"
    embed.description = "los invito a estudiar un entretenido curso de Pascal, un potententisimo lenguaje de programación: [CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT](https://www.youtube.com/watch?v=yvFCI2whgOA)."
    embed.color = embed.color = discord.Color.from_rgb(251, 141, 25)
    embed.set_thumbnail(
        url="https://jomerlisriera.files.wordpress.com/2015/03/lazarus_logo_new.png")
    await ctx.send(embed=embed)
    # await ctx.send('Hola mis estudiantes, vengan a estudiar conmigo, Pascal un potententisimo lenguaje de programación')
# https://www.youtube.com/watch?v=yvFCI2whgOA


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='[CSEC IT: Pascal Programming in 1 hour | MAKE IT SIMPLE TT]'), status=discord.Status.dnd)
    print(f'We have logged in as {bot.user}')


bot.run(token, log_handler=handler)
