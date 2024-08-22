import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import glob
import os
from mutagen.mp3 import MP3

from a_queue.audio_queue import AudioQueue


class AudioPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_queue = AudioQueue()
        self.is_playing_audio = False
        self.audio_directory = '/usr/home/users/fespinoza/bot_c/audio'

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
        if self.audio_queue.view_queue():
            queue_list = self.audio_queue.view_queue()
            queue_str = '\n'.join(
                [f"{idx + 1}. {os.path.basename(audio)}" for idx,
                 audio in enumerate(queue_list)]
            )
            embed = discord.Embed(
                title="Mi Cola", color=discord.Color.blurple())
            embed.description = queue_str
            await ctx.send(embed=embed)
        else:
            await ctx.send("No tengo nada en mi cola 😔.")

    @commands.command(help="Salta al siguiente audio en la cola de reproducción.")
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Audio saltado.")
        else:
            await ctx.send("No estoy reproduciendo ningún audio.")

    @commands.command(help="Elimina un audio de la cola de reproducción.")
    async def remove(self, ctx, index: int):
        try:
            removed_audio = self.audio_queue.remove_audio(index - 1)
            if removed_audio:
                await ctx.send(f"Audio en la posición {index} eliminado.")
            else:
                await ctx.send("Índice fuera de rango.")
        except IndexError:
            await ctx.send("Índice fuera de rango al intentar eliminar el audio.")

    @commands.command(help="Lista los archivos de audio disponibles.")
    async def list(self, ctx):
        embed = discord.Embed(
            title="Lista de reproducción disponible",
            description="Uso: !play fileName",
            color=0xFF5733
        )

        if not os.path.exists(self.audio_directory):
            await ctx.send("El directorio especificado no existe.")
            return

        files = os.listdir(self.audio_directory)

        if not files:
            await ctx.send("El directorio está vacío.")
            return

        for i, file in enumerate(files, start=1):
            file_path = os.path.join(self.audio_directory, file)
            if file.endswith('.mp3'):
                audio = MP3(file_path)
                duration = int(audio.info.length)
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes}:{seconds:02d}"
                file_name = file.split('.')[0]
                embed.add_field(name=f"{i}. {file_name}", value=f"Duración: {
                                duration_str}", inline=True)

        embed.set_footer(text="Lunes – Viernes: 6:00 – ??:??")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AudioPlayer(bot))
