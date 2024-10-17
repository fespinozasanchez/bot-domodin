import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import glob
import os
from mutagen.mp3 import MP3
from a_queue.audio_queue import AudioQueue
from utils.paginator_view import PaginatorView


class AudioPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_queue = AudioQueue()
        self.is_playing_audio = False
        self.audio_directory = '/root/bot-domodin/audio'

    @commands.command(help="Conecta al bot a un canal de voz.")
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("No estás conectado a ningún canal de voz.")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    @commands.command(help="Desconecta al bot de un canal de voz.")
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command(help="Reproduce un archivo de audio.")
    async def play(self, ctx, filename: str, repeat: int = 1):
        if ctx.voice_client is None:
            await ctx.send("No estoy conectado a un canal de voz.")
            return

        try:
            repeat = abs(int(repeat))
            if repeat < 1:
                raise ValueError
            repeat = min(repeat, 10)
        except ValueError:
            await ctx.send("Escribe el número correctamente, por favor.")
            return

        file_path = glob.glob(os.path.join(
            self.audio_directory, f"{filename}.*"))

        if not file_path:
            await ctx.send("El archivo especificado no existe.")
            return

        for _ in range(repeat):
            self.audio_queue.add(file_path[0])

        await ctx.send(f"Lo metí en mi cola {filename} repetido {repeat} veces")

        def play_next(error):
            if error:
                print(f"Error reproduciendo el audio: {error}")

            if self.audio_queue.view_queue() and self.is_playing_audio:
                next_audio = self.audio_queue.get_next_audio()
                print(f"Reproduciendo siguiente audio: {next_audio}")
                vc.play(FFmpegPCMAudio(next_audio), after=play_next)
            else:
                self.is_playing_audio = False

        vc = ctx.voice_client

        if not vc.is_connected():
            await ctx.send("El bot se desconectó del canal de voz.")
            self.is_playing_audio = False
            return

        self.is_playing_audio = True

        if not vc.is_playing():
            next_audio = self.audio_queue.get_next_audio()
            print(f"Reproduciendo audio: {next_audio}")
            vc.play(FFmpegPCMAudio(next_audio), after=play_next)
        else:
            print("Ya estoy reproduciendo audio.")

    @commands.command(help="Detiene la reproducción de audio actual.")
    async def stop(self, ctx):
        if ctx.voice_client is None:
            await ctx.send("No estoy conectado a un canal de voz.")
            return

        if ctx.voice_client.is_playing():
            self.is_playing_audio = False
            ctx.voice_client.stop()
            await ctx.send("Reproducción detenida.")
        else:
            await ctx.send("No estoy reproduciendo ningún audio.")

    @commands.command(help="Limpia la cola de reproducción.")
    async def clean(self, ctx):
        self.audio_queue.clean_queue()
        await ctx.send("Me limpié la cola.")

    @commands.command(help="Muestra la cola de reproducción.")
    async def q(self, ctx):
        queue_list = self.audio_queue.view_queue()
        if not queue_list:
            await ctx.send("No tengo nada en mi cola 😔.")
            return

        embeds = []
        page_size = 10  # 5 elementos por columna (10 en total por página)

        for i in range(0, len(queue_list), page_size):
            chunk = queue_list[i:i + page_size]
            embed = discord.Embed(
                title="Mi Cola", color=discord.Color.blurple())

            # Dividir el chunk en dos columnas
            half = len(chunk) // 2
            column1 = chunk[:half]
            column2 = chunk[half:]

            column1_text = '\n'.join([f"{i + idx + 1}. {os.path.basename(audio)}" for idx, audio in enumerate(column1)])
            column2_text = '\n'.join([f"{i + idx + half + 1}. {os.path.basename(audio)}" for idx, audio in enumerate(column2)])

            embed.add_field(name="Columna 1", value=column1_text or "─", inline=True)
            embed.add_field(name="Columna 2", value=column2_text or "─", inline=True)

            embeds.append(embed)

        if embeds:
            view = PaginatorView(embeds)
            await ctx.send(embed=embeds[0], view=view)

    @commands.command(help="Lista los archivos de audio disponibles.")
    async def list(self, ctx):
        if not os.path.exists(self.audio_directory):
            await ctx.send("El directorio especificado no existe.")
            return

        files = os.listdir(self.audio_directory)
        if not files:
            await ctx.send("El directorio está vacío.")
            return

        embeds = []
        page_size = 10  # 5 elementos por columna (10 en total por página)

        for i in range(0, len(files), page_size):
            chunk = files[i:i + page_size]
            embed = discord.Embed(
                title="Lista de reproducción disponible", color=0xFF5733)

            # Dividir el chunk en dos columnas
            half = len(chunk) // 2
            column1 = chunk[:half]
            column2 = chunk[half:]

            column1_text = ""
            column2_text = ""
            for idx, file in enumerate(column1):
                if file.endswith('.mp3'):
                    file_path = os.path.join(self.audio_directory, file)
                    audio = MP3(file_path)
                    duration = int(audio.info.length)
                    minutes, seconds = divmod(duration, 60)
                    duration_str = f"{minutes}:{seconds:02d}"
                    file_name = file.split('.')[0]
                    column1_text += f"{i + idx + 1}. {file_name} - ({duration_str})\n"

            for idx, file in enumerate(column2):
                if file.endswith('.mp3'):
                    file_path = os.path.join(self.audio_directory, file)
                    audio = MP3(file_path)
                    duration = int(audio.info.length)
                    minutes, seconds = divmod(duration, 60)
                    duration_str = f"{minutes}:{seconds:02d}"
                    file_name = file.split('.')[0]
                    column2_text += f"{i + idx + half + 1}. {file_name} - ({duration_str})\n"

            embed.add_field(name="Columna 1", value=column1_text or "─", inline=True)
            embed.add_field(name="Columna 2", value=column2_text or "─", inline=True)

            embeds.append(embed)

        if embeds:
            view = PaginatorView(embeds)
            await ctx.send(embed=embeds[0], view=view)


async def setup(bot):
    await bot.add_cog(AudioPlayer(bot))
