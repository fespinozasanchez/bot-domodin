import discord
from discord.ext import commands, tasks
from utils.natural_events_manager import get_current_natural_event, update_current_natural_event
from utils.market_data_manager import obtener_propiedades_por_color
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


                data= self.get_event_data_info()
                data_name= self.get_event_name()
                data_msg= data["msg"]
                data_tier= data["tier"][0]
                data_color= data["color"]
                if data_color == "all":
                    print('all')
                elif data_color == "blue":
                    print('blue')
                elif data_color == "red":
                    print('red')
                elif data_color == "orange":
                    print('orange')
                elif data_color == "purple":
                    print('purple')
                elif data_color == "pink":
                    print('pink')
                elif data_color == "yellow":
                    print('yellow')
            
        except Exception as e:
            logging.error(f"Error procesando el evento diario en {guild.name}:", exc_info=e)

    @daily_natural_event.before_loop
    async def before_daily_natural_event(self):
        await self.bot.wait_until_ready()

    @commands.Cog.listener()
    async def on_ready(self):
        logging.debug("Bot is ready. Verifying members registration...")
        for guild in self.bot.guilds:
            guild_id = str(guild.id)
            for member in guild.members:
                if not member.bot:
                    user_id = str(member.id)
                    key = f"{user_id}_{guild_id}"
                    if key not in self.data:
                        self.data[key] = {
                            'guild_id': guild_id, 'balance': 50000}
                        set_balance(user_id, guild_id, 50000)
        # Asegurarse de que siempre haya un evento actual al iniciar
        self.manejar_eventos_diarios(None, None)

async def setup(bot):
    await bot.add_cog(NaturalEvents(bot))