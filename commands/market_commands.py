import discord
from discord.ext import commands, tasks
from utils.custom_help import CustomHelpPaginator
from market_module.property_events import pagar_renta_diaria, despenalizar_propietario, pagar_costo_mantenimiento, pagar_costo_diario, aplicar_desgaste_automatico, comprar_propiedad, obtener_evento_global, mejorar_desgaste, vender_propiedad
from utils.market_data_manager import ( generar_propiedad,actualizar_estado_residencia_principal, obtener_propiedades_home, actualizar_estado_propiedad_arrendada, obtener_propiedades_por_usuario, obtener_saldo_usuario,
                                       guardar_propiedad, register_investor,obtener_usuarios_penalizados,
                                       verificar_estado_inversionista,es_inversionista,
                                       obtener_propiedad, obtener_usuarios_registrados)
import logging
from utils.channel_manager import save_channel_setting, load_channel_setting


class MarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ultima_propiedad_generada = None  # Para almacenar la última propiedad generada

        # Tareas automatizadas
        self.aplicar_desgaste.start()
        self.pago_renta_diaria.start()
        self.pago_diario.start()
        self.pago_mantenimiento.start()
        self.despenalizar_usuarios.start()

    # Comando: !registrar_inversionista
    @commands.command(name='registrar_inversionista', help='Registra al usuario como inversionista. Uso: !registrar_inversionista')
    async def registrar_inversionista(self, ctx):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)  # Usar guild_id para diferenciar servidores

        # Verificar si el usuario ya está registrado como inversionista
        if es_inversionista(usuario_id, guild_id):
            await ctx.send("Ya estás registrado como inversionista. No puedes registrarte de nuevo.")
            return

        # Generar propiedad inicial
        try:
            register_investor(usuario_id, guild_id)
            propiedad_inicial = generar_propiedad(tipo='hogar')
            propiedad_inicial["es_residencia_principal"] = True
            propiedad_inicial['usuario_id'] = usuario_id
            guardar_propiedad(propiedad_inicial)

            embed = discord.Embed(
                title="¡Registro exitoso!",
                description=f"Te has registrado como inversionista y has recibido una propiedad inicial tipo hogar: **{propiedad_inicial['nombre']}**.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Ocurrió un error al registrarte: {str(e)}")

    # Comando: !comprar_propiedad [tipo]
    @commands.command(name='comprar_propiedad', help="Compra una propiedad aleatoria del tipo especificado (hogar o tienda). Uso: !comprar_propiedad [tipo]")
    async def comprar_propiedad(self, ctx, tipo: str):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Validar tipo de propiedad
        if tipo not in ['hogar', 'tienda']:
            await ctx.send("Tipo de propiedad no válido. Usa 'hogar' o 'tienda'.")
            return

        try:
            # Generar una propiedad y comprobar el saldo
            propiedad = generar_propiedad(tipo)
            comprar_propiedad(usuario_id,guild_id, propiedad)
            await ctx.send(f"Has comprado una propiedad: {propiedad['nombre']}, nivel {propiedad['nivel']}.")
        except Exception as e:
            # Enviar mensaje de error al usuario
            await ctx.send(f"Error al comprar la propiedad: {str(e)}")

    # Comando: !ver_propiedad_hogar
    @commands.command(name='ver_propiedad_hogar', help='Muestra una propiedad tipo hogar disponible en el mercado.')
    async def ver_propiedad_hogar(self, ctx):
        propiedad = generar_propiedad('hogar')
        self.ultima_propiedad_generada = propiedad

        embed = discord.Embed(
            title="Propiedad Hogar en Venta",
            description=f"**{propiedad['nombre']}** está disponible para compra.",
            color=discord.Color.from_str(propiedad['color'])  # Usar el color de la propiedad
        )
        
        # Añadir más detalles de la propiedad con formato numérico
        embed.add_field(name="Valor de Compra", value=f"{float(propiedad['valor_compra']):,.2f}", inline=False)
        embed.add_field(name="Renta Diaria", value=f"{float(propiedad['renta_diaria']):,.2f}", inline=True)
        embed.add_field(name="Costo Diario", value=f"{float(propiedad['costo_diario']):,.2f}", inline=True)
        embed.add_field(name="Costo Mantenimiento", value=f"{float(propiedad['costo_mantenimiento']):,.2f}", inline=True)
        embed.add_field(name="Nivel", value=f"{propiedad['nivel']}", inline=True)
        embed.add_field(name="Tier", value=f"{propiedad['tier']}", inline=True)
        embed.add_field(name="Barrio", value=f"{propiedad['barrio']}", inline=True)
        embed.add_field(name="Tamaño", value=f"{propiedad['tamaño']}", inline=True)
        embed.add_field(name="Pisos", value=f"{propiedad['pisos']}", inline=True)
        embed.add_field(name="Desgaste", value=f"{propiedad['desgaste']}", inline=True)
        embed.add_field(name="Suerte", value=f"{propiedad['suerte']}", inline=True)

        await ctx.send(embed=embed)

    # Comando: !ver_propiedad_tienda
    @commands.command(name='ver_propiedad_tienda', help='Muestra una propiedad tipo tienda disponible en el mercado.')
    async def ver_propiedad_tienda(self, ctx):
        propiedad = generar_propiedad('tienda')
        self.ultima_propiedad_generada = propiedad

        embed = discord.Embed(
            title="Propiedad Tienda en Venta",
            description=f"**{propiedad['nombre']}** está disponible para compra.",
            color=discord.Color.from_str(propiedad['color'])  # Usar el color de la propiedad
        )

        # Añadir más detalles de la propiedad con formato numérico
        embed.add_field(name="Valor de Compra", value=f"{float(propiedad['valor_compra']):,.2f}", inline=False)
        embed.add_field(name="Renta Diaria", value=f"{float(propiedad['renta_diaria']):,.2f}", inline=True)
        embed.add_field(name="Costo Diario", value=f"{float(propiedad['costo_diario']):,.2f}", inline=True)
        embed.add_field(name="Costo Mantenimiento", value=f"{float(propiedad['costo_mantenimiento']):,.2f}", inline=True)
        embed.add_field(name="Nivel", value=f"{propiedad['nivel']}", inline=True)
        embed.add_field(name="Tier", value=f"{propiedad['tier']}", inline=True)
        embed.add_field(name="Barrio", value=f"{propiedad['barrio']}", inline=True)
        embed.add_field(name="Tamaño", value=f"{propiedad['tamaño']}", inline=True)
        embed.add_field(name="Pisos", value=f"{propiedad['pisos']}", inline=True)
        embed.add_field(name="Desgaste", value=f"{propiedad['desgaste']}", inline=True)
        embed.add_field(name="Suerte", value=f"{propiedad['suerte']}", inline=True)

        await ctx.send(embed=embed)

    # Comando: !comprar_propiedad_generada
    @commands.command(name='comprar_propiedad_generada', help='Compra la última propiedad generada en el mercado. Uso: !comprar_propiedad_generada')
    async def comprar_propiedad_generada(self, ctx):
        # Verificar si hay una propiedad generada
        if not self.ultima_propiedad_generada:
            await ctx.send("No hay ninguna propiedad generada. Usa !ver_propiedad_hogar o !ver_propiedad_tienda primero.")
            return

        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        propiedad = self.ultima_propiedad_generada

        try:
            # Intentar comprar la última propiedad generada
            comprar_propiedad(usuario_id, guild_id , propiedad)
            await ctx.send(f"Has comprado la propiedad {propiedad['nombre']} por {propiedad['valor_compra']}.")
            # Limpiar la última propiedad generada
            self.ultima_propiedad_generada = None
        except Exception as e:
            # Enviar mensaje de error si no pudo comprarse la propiedad
            await ctx.send(f"Error al comprar la propiedad generada: {str(e)}")

    # Comando: !vender_propiedad [propiedad_id]
    @commands.command(name='vender_propiedad', help='Vende una propiedad específica y recibe dinero según su valor.')
    async def vender_propiedad(self, ctx, propiedad_id: int):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        saldo_nuevo = vender_propiedad(usuario_id, guild_id, propiedad_id)
        if saldo_nuevo:
            await ctx.send(f"Has vendido la propiedad {propiedad_id}. Tu nuevo saldo es {saldo_nuevo}.")
        else:
            await ctx.send(f"No se encontró la propiedad o no eres el dueño.")
    
    # Comando: !global_event [propiedad_id]
    @commands.command(name='global_event', help='Ejecuta un evento global que afecta a todas las rentas.')
    async def global_event(self, ctx):
        event = obtener_evento_global()
        if event:
            await ctx.send(f"El evento actual es {event}")
        else:
            await ctx.send(f"No hay ningun evento actulamente.")

    # Comando: !listar_propiedades
    @commands.command(name='listar_propiedades', help='Lista todas tus propiedades.')
    async def listar_propiedades(self, ctx):
        usuario_id = str(ctx.author.id)
        propiedades = obtener_propiedades_por_usuario(usuario_id)

        if not propiedades:
            await ctx.send("No tienes propiedades.")
            return

        for propiedad in propiedades:
            embed = discord.Embed(
                title=f"Propiedad: {propiedad['nombre']}",
                description=f"Pequeña descripción de la propiedad.",
                color=discord.Color.from_str(propiedad['color'])  # Usar el color de la propiedad
            )

            # Añadir los campos con la información y el formato de los números
            embed.add_field(name="ID", value=f"{propiedad['id']}", inline=True)
            embed.add_field(name="Renta Diaria", value=f"{float(propiedad['renta_diaria']):,.2f}", inline=True)
            embed.add_field(name="Costo Diario", value=f"{float(propiedad['costo_diario']):,.2f}", inline=True)

            # Pie de página con una nota adicional
            embed.set_footer(text=f"Propiedad en el barrio {propiedad['barrio']} | Costo Mantenimiento: {float(propiedad['costo_mantenimiento']):,.2f} | Nivel: {propiedad['nivel']} | Tier: {propiedad['tier']} | Suerte: {propiedad['suerte']} | Desgaste: {propiedad['desgaste']}")

            # Enviar el embed como una "carta"
            await ctx.send(embed=embed)


    # Comando: !detalles_propiedad [propiedad_id]
    @commands.command(name='detalles_propiedad', help='Muestra los detalles de una propiedad específica.')
    async def detalles_propiedad(self, ctx, propiedad_id: int):
        propiedad = obtener_propiedad(propiedad_id)
        if propiedad:
            embed = discord.Embed(
                title=f"Detalles de la Propiedad: {propiedad['nombre']}",
                color=discord.Color.from_str(propiedad['color'])  # Usar el color de la propiedad
            )

            # Añadir campos con formato numérico para los valores monetarios
            embed.add_field(name="Tipo", value=propiedad['tipo'], inline=True)
            embed.add_field(name="Barrio", value=f"{propiedad['barrio']}", inline=True)
            embed.add_field(name="Nivel", value=f"{propiedad['nivel']}", inline=True)
            embed.add_field(name="Tier", value=f"{propiedad['tier']}", inline=True)
            embed.add_field(name="Renta Diaria", value=f"{float(propiedad['renta_diaria']):,.2f}", inline=True)
            embed.add_field(name="Costo Diario", value=f"{float(propiedad['costo_diario']):,.2f}", inline=True)
            embed.add_field(name="Costo Mantenimiento", value=f"{float(propiedad['costo_mantenimiento']):,.2f}", inline=True)
            embed.add_field(name="Suerte", value=f"{propiedad['suerte']}", inline=True)

            # Pie de página con alguna nota adicional
            embed.set_footer(text=f"Valor de compra: {float(propiedad['valor_compra']):,.2f} | Tamaño: {propiedad['tamaño']}m² | Piso/s: {propiedad['pisos']} | Desgaste: {propiedad['desgaste']} | Arrendada: {'Sí' if propiedad['arrendada'] else 'No'} | Residencia Principal: {'Sí' if propiedad['es_residencia_principal'] else 'No'}")

            await ctx.send(embed=embed)
        else:
            await ctx.send("No se encontró la propiedad.")

    # Comando: !mejorar_propiedad [propiedad_id], [cantidad melladocoins]
    @commands.command(name='mejorar_propiedad', help='Mejora el desgaste de una propiedad pagando una cantidad. Uso: !mejorar_propiedad [propiedad_id] [cantidad_pago]')
    async def mejorar_propiedad(self, ctx, propiedad_id: int, cantidad_pago: int):
        usuario_id = str(ctx.author.id)

        propiedad = obtener_propiedad(propiedad_id)

        if not propiedad:
            await ctx.send(f"No se encontró la propiedad con ID {propiedad_id}.")
            return

        if propiedad['usuario_id'] != usuario_id:
            await ctx.send("No tienes permisos para mejorar esta propiedad.")
            return

        if cantidad_pago <= 0:
            await ctx.send("La cantidad de MelladoCoins debe ser positiva.")
            return

        try:
            mejorar_desgaste(propiedad_id, cantidad_pago)
            await ctx.send(f"El desgaste de la propiedad con ID {propiedad_id} ha sido mejorado.")
        except Exception as e:
            await ctx.send(f"Ocurrió un error al mejorar la propiedad: {str(e)}")

    # Comando: !estado_inversionista
    @commands.command(name='estado_inversionista', help='Muestra el estado actual del inversionista.')
    async def estado_inversionista(self, ctx):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        estado = verificar_estado_inversionista(usuario_id)
        saldo = obtener_saldo_usuario(usuario_id, guild_id)

        if estado is not None:
            await ctx.send(f"Estado: Penalizado: {estado}, Saldo: {saldo}")
        else:
            await ctx.send("No estás registrado como inversionista.")

    # Comando: !renta_diaria
    @commands.command(name='renta_diaria', help='Muestra la renta diaria total de tus propiedades.')
    async def renta_diaria(self, ctx):
        usuario_id = str(ctx.author.id)
        propiedades = obtener_propiedades_por_usuario(usuario_id)

        renta_total = sum([propiedad['renta_diaria'] for propiedad in propiedades])
        await ctx.send(f"Tu renta diaria total es de {renta_total} MelladoCoins.")

    # Comando: !costo_diario
    @commands.command(name='costo_diario', help='Muestra el costo diario de todas tus propiedades.')
    async def costo_diario(self, ctx):
        usuario_id = str(ctx.author.id)
        propiedades = obtener_propiedades_por_usuario(usuario_id)

        costo_total = sum([propiedad['costo_diario'] for propiedad in propiedades])
        await ctx.send(f"Tu costo diario total es de {costo_total} MelladoCoins.")

    # Comando: !eventos_diarios
    @commands.command(name='eventos_diarios', help='Muestra los eventos globales que afectan las rentas diarias.')
    async def eventos_diarios(self, ctx):
        evento = obtener_evento_global()
        if evento:
            await ctx.send(f"Evento actual: {evento}")
        else:
            await ctx.send("No hay eventos activos por el momento.")

    # Comando: !ver_penalizacion [usuario_id]
    @commands.command(name='ver_penalizacion', help='Consulta el estado de penalización de un usuario.')
    async def ver_penalizacion(self, ctx, usuario_id: int):
        estado = verificar_estado_inversionista(usuario_id)

        if estado:
            await ctx.send(f"El usuario {usuario_id} está penalizado.")
        else:
            await ctx.send(f"El usuario {usuario_id} no está penalizado.")

    # Comando: !arrendar_propiedad [propiedad_id]
    @commands.command(name='arrendar_propiedad', help='Arrenda una propiedad tipo hogar. Uso: !arrendar_propiedad [propiedad_id]')
    async def arrendar_propiedad(self, ctx, propiedad_id: int):
        usuario_id = str(ctx.author.id)
        propiedad = obtener_propiedad(propiedad_id)

        if not propiedad:
            await ctx.send(f"No se encontró la propiedad con ID {propiedad_id}.")
            return

        if propiedad['usuario_id'] != usuario_id:
            await ctx.send("No tienes permisos para arrendar esta propiedad.")
            return

        if propiedad['tipo'] != 'hogar':
            await ctx.send("Solo puedes arrendar propiedades de tipo hogar.")
            return

        # Si la propiedad es la residencia principal
        if propiedad['es_residencia_principal']:
            # Verificar si el usuario tiene otras propiedades hogar marcadas como residencia principal
            propiedades_home = obtener_propiedades_home(usuario_id)
            if len(propiedades_home) <= 1:
                await ctx.send("No puedes arrendar tu residencia principal porque no tienes otra propiedad hogar marcada como residencia principal.")
                return

        if propiedad['arrendada']:
            await ctx.send(f"La propiedad {propiedad['nombre']} ya está arrendada.")
            return

        try:
            # Establecer la propiedad como arrendada y quitar el estado de residencia principal
            actualizar_estado_propiedad_arrendada(propiedad_id, arrendada=True)
            actualizar_estado_residencia_principal(propiedad_id, es_residencia_principal=False)
            await ctx.send(f"La propiedad {propiedad['nombre']} ha sido arrendada.")
        except Exception as e:
            await ctx.send(f"Ocurrió un error al arrendar la propiedad: {str(e)}")

    # Comando: !establecer_residencia_principal [propiedad_id]
    @commands.command(name='establecer_residencia_principal', help='Establece una propiedad hogar como residencia principal. Uso: !establecer_residencia_principal [propiedad_id]')
    async def establecer_residencia_principal(self, ctx, propiedad_id: int):
        usuario_id = str(ctx.author.id)
        propiedad = obtener_propiedad(propiedad_id)

        if not propiedad:
            await ctx.send(f"No se encontró la propiedad con ID {propiedad_id}.")
            return

        if propiedad['usuario_id'] != usuario_id:
            await ctx.send("No tienes permisos para modificar esta propiedad.")
            return

        if propiedad['tipo'] != 'hogar':
            await ctx.send("Solo puedes establecer propiedades de tipo hogar como residencia principal.")
            return

        # Actualizar la propiedad seleccionada como residencia principal
        try:
            # Marcar la propiedad como no arrendada
            if propiedad['arrendada']:
                actualizar_estado_propiedad_arrendada(propiedad_id, arrendada=False)

            # Buscar todas las propiedades hogar actuales y quitar el estado de residencia principal
            propiedades_home = obtener_propiedades_por_usuario(usuario_id)
            for prop in propiedades_home:
                if prop['tipo'] == 'hogar' and prop['es_residencia_principal']:
                    actualizar_estado_residencia_principal(prop['id'], es_residencia_principal=False)

            # Establecer la propiedad seleccionada como residencia principal
            actualizar_estado_residencia_principal(propiedad_id, es_residencia_principal=True)
            await ctx.send(f"La propiedad {propiedad['nombre']} ha sido establecida como tu residencia principal.")
        except Exception as e:
            await ctx.send(f"Ocurrió un error al establecer la residencia principal: {str(e)}")



    # Comando: !home
    @commands.command(name='home', help='Lista todas tus propiedades tipo hogar que son tu residencia principal.')
    async def home(self, ctx):
        usuario_id = str(ctx.author.id)
        propiedades_home = obtener_propiedades_home(usuario_id)

        if not propiedades_home:
            await ctx.send("No tienes ninguna propiedad marcada como residencia principal.")
            return

        descripcion = "**Tus Propiedades Hogar:**\n"
        for propiedad in propiedades_home:
            descripcion += f"ID: {propiedad['id']}, Nombre: {propiedad['nombre']}, Renta Diaria: {propiedad['renta_diaria']}, Costo Diario: {propiedad['costo_diario']}, Costo Mantenimiento: {propiedad['costo_mantenimiento']}\n"
        await ctx.send(descripcion)



    # --- Funciones automáticas con loop ---

    # Función para enviar notificaciones a un canal específico
    async def enviar_notificacion(self, guild_id, mensaje):
        channel_id = load_channel_setting(guild_id)  # Cargar la configuración del canal
        channel = self.bot.get_channel(channel_id)

        # Verificar si el canal existe y tiene permisos
        if not channel or not channel.permissions_for(channel.guild.me).send_messages:
            guild = self.bot.get_guild(int(guild_id))
            # Seleccionar un canal nuevo si el configurado ya no es válido
            channel = next((c for c in guild.text_channels if c.permissions_for(guild.me).send_messages), None)
            if channel:
                save_channel_setting(guild_id, channel.id)  # Guardar el nuevo canal
            else:
                logging.warning(f"No hay canales disponibles para enviar mensajes en {guild.name}.")
                return
        
        await channel.send(mensaje)

    # Aplicar desgaste a las propiedades cada 7 días
    @tasks.loop(hours=168)  # Cada 7 días
    async def aplicar_desgaste(self):
        logging.info("Iniciando la tarea de aplicar desgaste.")
        usuarios = obtener_usuarios_registrados()

        if not usuarios:
            logging.info("No se encontraron usuarios registrados para aplicar desgaste.")
            return

        for usuario in usuarios:
            propiedades = obtener_propiedades_por_usuario(usuario['usuario_id'])
            for propiedad in propiedades:
                aplicar_desgaste_automatico(propiedad)
                logging.info(f"Desgaste aplicado a la propiedad {propiedad['nombre']} del usuario {usuario['usuario_id']}.")

        # Notificación de desgaste aplicado solo a servidores con inversionistas
        for guild in self.bot.guilds:
            if any(usuario for usuario in usuarios if str(usuario['guild_id']) == str(guild.id)):
                await self.enviar_notificacion(guild.id, "¡Se ha aplicado el desgaste a todas las propiedades!")
                logging.info(f"Notificación enviada al servidor {guild.name}.")


    # Pago de renta diaria cada día
    @tasks.loop(hours=24)  # Cada día
    async def pago_renta_diaria(self):
        logging.info("Iniciando la tarea de pago de renta diaria.")
        
        # Obtener todos los usuarios registrados (incluyendo guild_id)
        usuarios = obtener_usuarios_registrados()

        if not usuarios:
            logging.info("No se encontraron usuarios registrados para pagar renta diaria.")
            return

        # Pagar la renta diaria a cada usuario por servidor
        for usuario in usuarios:
            guild_id = usuario['guild_id']
            usuario_id = usuario['usuario_id']
            pagar_renta_diaria(usuario_id, guild_id)  # Pasar guild_id como argumento
            logging.info(f"Renta diaria pagada al usuario {usuario_id} en el servidor {guild_id}.")

        # Notificación de rentas pagadas solo a servidores con inversionistas
        for guild in self.bot.guilds:
            if any(usuario for usuario in usuarios if str(usuario['guild_id']) == str(guild.id)):
                await self.enviar_notificacion(guild.id, "¡Se han pagado las rentas diarias!")
                logging.info(f"Notificación de pago de rentas enviada al servidor {guild.name}.")



    # Pago de mantenimiento cada 3 días
    @tasks.loop(hours=72)  # Cada 3 días
    async def pago_mantenimiento(self):
        logging.info("Iniciando la tarea de pago de mantenimiento.")
        
        # Obtener todos los usuarios registrados (con su guild_id)
        usuarios = obtener_usuarios_registrados()

        if not usuarios:
            logging.info("No se encontraron usuarios registrados para pagar el mantenimiento.")
            return

        # Pagar el costo de mantenimiento para cada usuario y servidor (guild)
        for usuario in usuarios:
            guild_id = usuario['guild_id']
            usuario_id = usuario['usuario_id']
            pagar_costo_mantenimiento(usuario_id, guild_id)  # Pasa el guild_id también
            logging.info(f"Pago de mantenimiento realizado para el usuario {usuario_id} en el servidor {guild_id}.")

        # Notificación de pago de mantenimiento solo a servidores con inversionistas
        for guild in self.bot.guilds:
            # Verificar si el servidor tiene inversionistas registrados
            if any(usuario for usuario in usuarios if str(usuario['guild_id']) == str(guild.id)):
                await self.enviar_notificacion(guild.id, "¡Se ha pagado el costo de mantenimiento de las propiedades!")
                logging.info(f"Notificación de pago de mantenimiento enviada al servidor {guild.name}.")



    # Cobro de costos diarios cada día
    @tasks.loop(hours=24)  # Cada día
    async def pago_diario(self):
        logging.info("Iniciando la tarea de cobro de costos diarios.")
        
        # Obtener todos los usuarios registrados (incluyendo guild_id)
        usuarios = obtener_usuarios_registrados()

        if not usuarios:
            logging.info("No se encontraron usuarios registrados para cobrar los costos diarios.")
            return

        # Cobrar el costo diario a cada usuario por servidor
        for usuario in usuarios:
            guild_id = usuario['guild_id']
            usuario_id = usuario['usuario_id']
            pagar_costo_diario(usuario_id, guild_id)  # Pasar guild_id como argumento
            logging.info(f"Costo diario cobrado al usuario {usuario_id} en el servidor {guild_id}.")

        # Notificación de costos diarios cobrados solo a servidores con inversionistas
        for guild in self.bot.guilds:
            if any(usuario for usuario in usuarios if str(usuario['guild_id']) == str(guild.id)):
                await self.enviar_notificacion(guild.id, "¡Se han cobrado los costos diarios de las propiedades!")
                logging.info(f"Notificación de cobro de costos diarios enviada al servidor {guild.name}.")


    @tasks.loop(hours=72)  # Cada 3 días - Despenalización de usuarios
    async def despenalizar_usuarios(self):
        logging.info("Iniciando la tarea de despenalización de usuarios.")
        usuarios = obtener_usuarios_penalizados()

        # Corroborar si hay usuarios penalizados antes de proceder
        if not usuarios:
            logging.info("No hay usuarios penalizados para despenalizar.")
            return

        # Despenalizar usuarios penalizados
        for usuario in usuarios:
            despenalizar_propietario(usuario['usuario_id'])
            logging.info(f"El usuario {usuario['usuario_id']} ha sido despenalizado.")

        # Enviar notificación solo a servidores con usuarios penalizados
        for guild in self.bot.guilds:
            if any(str(usuario['guild_id']) == str(guild.id) for usuario in usuarios):
                await self.enviar_notificacion(guild.id, "¡Se ha despenalizado a los usuarios!")
                logging.info(f"Notificación de despenalización enviada al servidor {guild.name}.")


    # --- Funciones auxiliares ---
    
    async def verificar_inversionista(self, ctx):
        usuario_id = str(ctx.author.id)
        if not es_inversionista(usuario_id):
            await ctx.send("Debes estar registrado como inversionista para usar este comando. Usa !registrar_inversionista.")
            return False
        return True

# Setup para agregar el cog al bot
async def setup(bot):
    await bot.add_cog(MarketCommands(bot))
