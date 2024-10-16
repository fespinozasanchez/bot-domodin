import discord
from discord.ext import commands, tasks
from utils.natural_events_manager import get_current_natural_event, update_current_natural_event, get_events_date
from utils.market_data_manager import eliminar_propiedad, obtener_propiedades_por_color, obtener_propiedades_por_usuario
from utils.data_manager import load_all_users, load_user_data, save_user_data, set_balance
from market_module.const_market import COLORS
from .natural_events_const import EVENTS
from datetime import datetime, timedelta
import logging
import random as ra
from utils.channel_manager import save_channel_setting, load_channel_setting
from discord import app_commands

logging.basicConfig(level=logging.DEBUG)


class NaturalEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_all_users()
        self.daily_natural_event.start()
        self._event_name = None
        self._event_data = None

    @property
    def event_name(self):
        return self._event_name

    @event_name.setter
    def event_name(self, value):
        self._event_name = value

    @property
    def event_data(self):
        return self._event_data

    @event_data.setter
    def event_data(self, value):
        self._event_data = value

    @staticmethod
    def get_event_chance():
        return ra.choices(list(EVENTS.keys()), [v["chance"] for v in EVENTS.values()])[0]

    @classmethod
    def get_event_data(cls, event_chance):
        return EVENTS[event_chance]

    def manejar_eventos_diarios(self, evento_actual, fecha_cambio):
        try:
            # Obtener el evento actual desde la base de datos
            resultado_evento = get_current_natural_event()
            if resultado_evento is None:
                logging.warning("No se encontró ningún evento en la base de datos. Se creará uno nuevo.")
                # Generar y guardar un nuevo evento si no existe ninguno
                evento_aleatorio = self.get_event_chance()
                nuevo_evento = self.get_event_data(evento_aleatorio)

                # Asignar los valores a los atributos de la clase
                self.event_name = evento_aleatorio
                self.event_data = nuevo_evento

                update_current_natural_event(evento_aleatorio, datetime.now())
                return

            evento_actual = resultado_evento['current_event']
            fecha_cambio = resultado_evento['updated_at']
            self.event_name = evento_actual
            self.event_data = self.get_event_data(evento_actual)
        except Exception as e:
            logging.error(f"Error al obtener el evento global actual: {e}")
            return

        # Convertir la fecha de cambio a datetime si es necesario
        try:
            if isinstance(fecha_cambio, str):
                fecha_cambio = datetime.strptime(fecha_cambio, "%Y-%m-%d %H:%M:%S")
        except ValueError as ve:
            logging.error(f"Error al convertir la fecha de cambio del evento global a datetime: {ve}")
            return

        ahora = datetime.now()

        try:
            # Si han pasado más de 4 horas, cambiar el evento
            if ahora - fecha_cambio >= timedelta(hours=4):
                evento_aleatorio = self.get_event_chance()  # Obtener el evento aleatorio
                nuevo_evento = self.get_event_data(evento_aleatorio)  # Obtener los datos del evento aleatorio
                self.event_name = evento_aleatorio
                self.event_data = nuevo_evento
                try:
                    # Actualizar el evento global en la base de datos
                    update_current_natural_event(evento_aleatorio, ahora)
                    logging.info(f"El evento global ha cambiado a: {nuevo_evento['msg']}")
                except Exception as e:
                    logging.error(f"Error al actualizar el evento global: {e}")
            else:
                logging.info(f"El evento global actual es: {evento_actual}")
        except Exception as e:
            logging.error(f"Error al manejar los eventos diarios: {e}")

    @tasks.loop(hours=1)
    async def daily_natural_event(self):
        try:
            # Obtener el evento actual desde la base de datos
            resultado_evento = get_current_natural_event()
            if resultado_evento is None:
                logging.info("No se encontraron eventos naturales activos.")
                # Generar un evento inicial si no hay ninguno
                self.generar_nuevo_evento()
                return

            # Extraer la información del evento y su fecha de actualización
            evento_actual = resultado_evento['current_event']
            fecha_cambio = resultado_evento['updated_at']

            # Convertir fecha_cambio a datetime si es una cadena
            if isinstance(fecha_cambio, str):
                fecha_cambio = datetime.strptime(fecha_cambio, "%Y-%m-%d %H:%M:%S")

            ahora = datetime.now()

            # Verificar si han pasado 24 horas desde el último evento
            if ahora - fecha_cambio >= timedelta(hours=24):
                # Generar un nuevo evento y actualizar la base de datos
                self.generar_nuevo_evento()
            else:
                logging.info(f"El evento natural actual es: {evento_actual}, aún no han pasado 24 horas.")
        except Exception as e:
            logging.error(f"Error procesando el evento diario: {e}")

    def generar_nuevo_evento(self):
        evento_aleatorio = self.get_event_chance()
        nuevo_evento = self.get_event_data(evento_aleatorio)
        self.event_name = evento_aleatorio
        self.event_data = nuevo_evento

        # Actualizar el evento en la base de datos
        update_current_natural_event(evento_aleatorio, datetime.now())
        logging.info(f"El evento natural ha cambiado a: {self.event_name}")

        # Enviar el mensaje del evento a los canales correspondientes, pasando también el nombre
        self.bot.loop.create_task(self.enviar_evento_a_canales(evento_aleatorio, nuevo_evento))

    async def enviar_evento_a_canales(self, evento_nombre, evento):
        """
        Envía el mensaje del evento natural a todos los servidores configurados.
        """
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            channel_id = load_channel_setting(guild_id)

            # Configurar el canal si no está definido
            if channel_id is None:
                channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                if channel:
                    channel_id = channel.id
                    save_channel_setting(guild_id, channel_id)
                else:
                    logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                    continue
            else:
                channel = self.bot.get_channel(channel_id)
                if not channel or not channel.permissions_for(guild.me).send_messages:
                    channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                    if channel:
                        channel_id = channel.id
                        save_channel_setting(guild_id, channel_id)
                    else:
                        logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                        continue

            # Crear el embed para el evento, usando el nombre del evento directamente
            embed = discord.Embed(
                title=f"Evento Natural: {evento_nombre}",
                description=evento['msg'],
                color=discord.Color.red()
            )
            embed.set_image(url=evento['url'])
            embed.add_field(name="Nivel de impacto (Tier)", value=str(evento['tier'][0]), inline=False)

            await channel.send(embed=embed)

    @daily_natural_event.before_loop
    async def before_daily_natural_event(self):
        await self.bot.wait_until_ready()

    @commands.command(name='ver_evento', help="Muestra el evento natural actual")
    async def ver_evento(self, ctx):
        await self._ver_evento(ctx)

    # Slash Command
    @app_commands.command(name='ver_evento', description='Muestra el evento natural actual')
    async def slash_ver_evento(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._ver_evento(ctx)

    async def _ver_evento(self, ctx):
        try:
            resultado_evento = get_current_natural_event()
            if resultado_evento is None:
                await ctx.send("No se encontraron eventos naturales activos.")
                return

            evento_actual = resultado_evento['current_event']
            fecha_cambio = resultado_evento['updated_at']
            self.manejar_eventos_diarios(evento_actual, fecha_cambio)

            evento = self.event_data
            evento_nombre = self.event_name
            evento_tier = evento["tier"][0]
            evento_msg = evento["msg"].format(propiedades=evento_tier)
            evento_color = evento["color"]

            embed = discord.Embed(
                title=f"Evento Natural: {evento_nombre}",
                description=evento_msg,
                color=discord.Color.red()
            )
            embed.set_image(url=evento["url"])
            embed.add_field(name="Nivel de impacto (Tier)", value=str(evento_tier), inline=False)

            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error al ver el evento global actual:", exc_info=e)

    @commands.Cog.listener()
    async def on_ready(self):
        logging.debug("Bot is ready. Verifying members registration...")
        # Asegurarse de que siempre haya un evento actual al iniciar
        self.manejar_eventos_diarios(None, None)


async def setup(bot):
    await bot.add_cog(NaturalEvents(bot))
