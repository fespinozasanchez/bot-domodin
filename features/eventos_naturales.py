import discord
from discord.ext import commands, tasks
from utils.natural_events_manager import get_current_natural_event, update_current_natural_event
from utils.market_data_manager import eliminar_propiedad, obtener_propiedades_por_color, obtener_propiedades_por_usuario
from utils.data_manager import load_all_users, load_user_data, save_user_data, set_balance
from market_module.const_market import COLORS
from .natural_events_const import EVENTS
from datetime import datetime, timedelta
import logging
import random as ra
from utils.channel_manager import save_channel_setting, load_channel_setting

logging.basicConfig(level=logging.DEBUG)


class NaturalEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_all_users()
        self.daily_natural_event.start()
        self.event_name = None
        self.event_data = None

    def set_event_name(self, event_name):
        self.event_name = event_name

    def set_event_data(self, event_data):
        self.event_data = event_data

    def get_event_name(self):
        return self.event_name

    def get_event_data_info(self):
        return self.event_data

    @staticmethod
    def get_event_chance():
        return ra.choices(list(EVENTS.keys()), [v["chance"] for v in EVENTS.values()])[0]

    @classmethod
    def get_event_data(cls, event_chance):
        return EVENTS[event_chance]

    @staticmethod
    def get_event_tier(event_data):
        return ra.choices(event_data["tier"], event_data["tier_weight"])[0]

    def manejar_eventos_diarios(self, evento_actual, fecha_cambio):
        try:
            # Obtener el evento actual desde la base de datos
            resultado_evento = get_current_natural_event()
            if resultado_evento is None:
                logging.warning("No se encontró ningún evento en la base de datos. Se creará uno nuevo.")
                # Generar y guardar un nuevo evento si no existe ninguno
                evento_aleatorio = self.get_event_chance()
                nuevo_evento = self.get_event_data(evento_aleatorio)
                self.set_event_name(evento_aleatorio)
                self.set_event_data(nuevo_evento)
                update_current_natural_event(evento_aleatorio, datetime.now())
                return

            evento_actual = resultado_evento['current_event']
            fecha_cambio = resultado_evento['updated_at']
            self.set_event_name(evento_actual)
            self.set_event_data(self.get_event_data(evento_actual))
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
                self.set_event_name(evento_aleatorio)
                self.set_event_data(nuevo_evento)
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

    @tasks.loop(hours=24)
    async def daily_natural_event(self):
        try:
            for guild in self.bot.guilds:
                guild_id = str(guild.id)
                channel_id = load_channel_setting(guild_id)  # Cargar la configuración del canal

                # Si no hay un canal configurado, selecciona el primer canal disponible
                if channel_id is None:
                    channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                    if channel:
                        channel_id = channel.id
                        save_channel_setting(guild_id, channel_id)  # Guarda este canal como el predeterminado
                    else:
                        logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                        continue
                else:
                    channel = self.bot.get_channel(channel_id)
                    if not channel or not channel.permissions_for(guild.me).send_messages:
                        channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
                        if channel:
                            channel_id = channel.id
                            save_channel_setting(guild_id, channel_id)  # Guarda este nuevo canal como el predeterminado
                        else:
                            logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                            continue

                # Obtener los datos del evento actual
                data = self.get_event_data_info()
                data_name = self.get_event_name()
                data_tier = self.get_event_tier(data)
                data_msg = data["msg"].format(propiedades=data_tier)
                data_color = data["color"]

                # Crear un embed con la información del evento
                embed = discord.Embed(
                    title=f"Evento Natural: {data_name}",
                    description=data_msg,
                    color=discord.Color.red()
                )
                embed.set_image(url=data["url"])
                embed.add_field(name="Nivel de impacto (Tier)", value=str(data_tier), inline=False)

                if data_name != "Domingo de Diosito":
                    # Realizar acciones dependiendo del color afectado
                    propiedades_afectadas = obtener_propiedades_por_color(data_color) if data_color != "all" else obtener_propiedades_por_color(None)
                    for propiedad in propiedades_afectadas:
                        user_id = propiedad['inversionista_id']
                        propiedades_usuario = obtener_propiedades_por_usuario(user_id)

                        # Filtrar propiedades que coinciden con el color afectado si no es "all"
                        propiedades_dañadas = [p for p in propiedades_usuario if p['color'] == data_color] if data_color != "all" else propiedades_usuario
                        propiedades_destruidas = min(len(propiedades_dañadas), data_tier)  # Destruir propiedades según el tier

                        # Eliminar las propiedades destruidas de la lista de propiedades del usuario
                        propiedades_eliminadas = propiedades_dañadas[:propiedades_destruidas]
                        for propiedad in propiedades_eliminadas:
                            print(f'Eliminando propiedad {propiedad["id"]} del usuario: {user_id}')
                            eliminar_propiedad(propiedad['id'])

                        logging.warning(f"{propiedades_destruidas} propiedades de color {data_color} fueron destruidas para el usuario {user_id}")

                # Enviar el embed al canal correspondiente
                await channel.send(embed=embed)

        except Exception as e:
            logging.error(f"Error procesando el evento diario en {guild.name}:", exc_info=e)

    @daily_natural_event.before_loop
    async def before_daily_natural_event(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        logging.debug("Bot is ready. Verifying members registration...")
        # Asegurarse de que siempre haya un evento actual al iniciar
        self.manejar_eventos_diarios(None, None)


async def setup(bot):
    await bot.add_cog(NaturalEvents(bot))
