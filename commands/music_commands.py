import discord
from discord import FFmpegPCMAudio
import glob
import os
from mutagen.mp3 import MP3
from a_queue.audio_queue import AudioQueue


def register_commands(bot, audio_queue):

    @bot.command(help="Conecta al bot a un canal de voz.")
    async def join(ctx):
        if ctx.author.voice is None:
            await ctx.send("No estas conectado a ningun canal de voz")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    @bot.command(help="Desconecta al bot de un canal de voz.")
    async def leave(ctx):
        await ctx.voice_client.disconnect()

    @bot.command(help="Reproduce un archivo de audio.")
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

        await ctx.send(f"Lo metí en mi cola {filename} repetido {repeat} veces")

        def play_next(error):
            if error:
                print(f"Error reproduciendo el audio: {error}")

            if audio_queue.view_queue() and bot.is_playing_audio:
                next_audio = audio_queue.get_next_audio()
                print(f"Reproduciendo siguiente audio: {next_audio}")
                vc.play(FFmpegPCMAudio(next_audio), after=play_next)
            else:
                bot.is_playing_audio = False

        vc = ctx.voice_client

        if not vc.is_connected():
            await ctx.send("El bot se desconectó del canal de voz.")
            bot.is_playing_audio = False
            return

        bot.is_playing_audio = True

        if not vc.is_playing():
            next_audio = audio_queue.get_next_audio()
            print(f"Reproduciendo audio: {next_audio}")
            vc.play(FFmpegPCMAudio(next_audio), after=play_next)
        else:
            print("Ya estoy reproduciendo audio.")

    @bot.command(help="Detiene la reproducción de audio actual.")
    async def stop(ctx):
        if ctx.voice_client is None:
            await ctx.send("No estoy conectado a un canal de voz")
            return

        if ctx.voice_client.is_playing():
            bot.is_playing_audio = False
            ctx.voice_client.stop()
            await ctx.send("Reproducción detenida.")
        else:
            await ctx.send("No estoy reproduciendo ningún audio.")

    @bot.command(help="Limpiar la cola de reproducción.")
    async def clean(ctx):
        audio_queue.clean_queue()
        await ctx.send("Me limpie la colita 🥰")

    @bot.command(help="Muestra la cola de reproducción.")
    async def q(ctx):
        if audio_queue.view_queue():
            queue_list = audio_queue.view_queue()
            queue_str = '\n'.join(
                [f"{idx + 1}. {os.path.basename(audio)}" for idx, audio in enumerate(queue_list)])
            embed = discord.Embed(
                title="Mi Cola ", color=discord.Color.blurple())
            embed.description = queue_str
            await ctx.send(embed=embed)
        else:
            await ctx.send("No tengo nada en mi  cola 😔.")

    @bot.command(help="Salta al siguiente audio en la cola de reproducción.")
    async def skip(ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Audio saltado.")
        else:
            await ctx.send("No estoy reproduciendo ningún audio.")

    @bot.command(help="Elimina un audio de la cola de reproducción.")
    async def remove(ctx, index: int):
        try:
            audio_queue.remove_audio(index - 1)
            await ctx.send(f"Audio en la posición {index} eliminado.")
        except IndexError:
            await ctx.send("Índice fuera de rango al intentar eliminar audio.")

    @bot.command(help="Lista los archivos de audio disponibles.")
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
                embed.add_field(name="", value=f'{i}. {
                                file_name} - ({duration_str})', inline=True)

                i += 1

        embed.set_footer(text="Lunes – Viernes: 6:00 – ??:??")
        embed.set_thumbnail(
            url="https://media.licdn.com/dms/image/C5603AQHFwyRGQtuSUA/profile-displayphoto-shrink_200_200/0/1516997163523?e=2147483647&v=beta&t=WtAtj17uSKfW4cIb1Ki8o4fBeqXTOnR4qooq9wSb8zI")
        await ctx.send(embed=embed)
