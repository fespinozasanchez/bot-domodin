import discord
from discord.ext import commands, tasks
from utils.custom_help import CustomHelpPaginator
from datetime import datetime, timedelta
import pytz
from market_module.property_events import (pagar_renta_diaria, despenalizar_propietario, pagar_costo_mantenimiento,
                                           pagar_costo_diario, aplicar_desgaste_automatico, comprar_propiedad,
                                           obtener_evento_global, mejorar_desgaste, vender_propiedad)
from utils.market_data_manager import (actualizar_desgaste_propiedad, actualizar_fecha_tarea, generar_propiedad, actualizar_estado_residencia_principal, get_user_inversionista, obtener_id_inversionista, obtener_pagos,
                                       obtener_propiedades_home, actualizar_estado_propiedad_arrendada,
                                       obtener_propiedades_por_usuario, obtener_saldo_usuario, guardar_propiedad, obtener_usuarios_con_fecha,
                                       register_investor, obtener_usuarios_penalizados, verificar_estado_inversionista,
                                       es_inversionista, obtener_propiedad, obtener_usuarios_registrados)
import logging
from utils.channel_manager import save_channel_setting, load_channel_setting
from discord import app_commands


class MarketCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tree = bot.tree
        self.ultima_propiedad_generada = None  # Para almacenar la última propiedad generada

        # Tareas automatizadas
        self.aplicar_desgaste.start()
        self.pago_renta_diaria.start()
        self.pago_diario.start()
        self.pago_mantenimiento.start()
        # self.despenalizar_usuarios.start()

    # Comando con prefijo
    @commands.command(name='registrar_inversionista', help='Registra al usuario como inversionista. Uso: !registrar_inversionista')
    async def registrar_inversionista(self, ctx):
        await self._registrar_inversionista(ctx)

    @app_commands.command(name='registrar_inversionista', description='Registra al usuario como inversionista')
    async def slash_registrar_inversionista(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._registrar_inversionista(ctx)

    # Función compartida por ambos comandos

    async def _registrar_inversionista(self, ctx):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Verificamos si el usuario ya está registrado como inversionista
        if es_inversionista(usuario_id, guild_id):
            embed = discord.Embed(
                title="¡Registro Fallido!",
                description="Ya estás registrado como inversionista.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

        try:
            # Registramos al usuario como inversionista y obtenemos su ID
            user_id = register_investor(usuario_id, guild_id)

            propiedad_inicial = generar_propiedad(tipo='hogar')
            propiedad_inicial["es_residencia_principal"] = True
            propiedad_inicial['usuario_id'] = user_id

            # Guardamos la propiedad asociada al usuario registrado
            guardar_propiedad(propiedad_inicial)

            # Enviamos un mensaje de éxito
            embed = discord.Embed(
                title="¡Registro exitoso!",
                description=f"Te has registrado como inversionista y has recibido una propiedad inicial tipo hogar: **{propiedad_inicial['nombre']}**.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

        except Exception as e:
            # Enviamos un mensaje de éxito
            logging.error(f"Error al registrar al inversionista: {str(e)}")
            embed = discord.Embed(
                title="¡Registro Fallido!",
                description=f"Ocurrió un error al registrarte como inversionista.\nPor favor, intenta nuevamente.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !comprar_propiedad [tipo]

    @commands.command(name='comprar_propiedad', help="Compra una propiedad aleatoria del tipo especificado (hogar o tienda). Uso: !comprar_propiedad [tipo]")
    async def comprar_propiedad(self, ctx, tipo: str):
        await self._comprar_propiedad(ctx, tipo)

    # Slash Command
    @app_commands.command(name='comprar_propiedad', description='Compra una propiedad aleatoria del tipo especificado')
    async def slash_comprar_propiedad(self, interaction: discord.Interaction, tipo: str):
        ctx = await commands.Context.from_interaction(interaction)
        await self._comprar_propiedad(ctx, tipo)

    async def _comprar_propiedad(self, ctx, tipo: str):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        # Validar tipo de propiedad
        if tipo not in ['hogar', 'tienda']:
            await ctx.send("Tipo de propiedad no válido. Usa 'hogar' o 'tienda'.")
            return

        if not es_inversionista(usuario_id, guild_id):
            embed = discord.Embed(
                title="¡Compra Fallida!",
                description="No estás registrado como inversionista. Usa **/registrar_inversionista** para registrarte.",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=embed)
            return

        try:
            propiedad = generar_propiedad(tipo)
            user_id = obtener_id_inversionista(usuario_id, guild_id)
            propiedad['usuario_id'] = user_id
            comprar_propiedad(usuario_id, guild_id, propiedad)
            embed = discord.Embed(
                title="¡Compra Exitosa!",
                description=f"Has comprado una propiedad: **{propiedad['nombre']}** de tipo **{tipo}** y nivel **{propiedad['nivel']}**.",
                color=discord.Color.green(),
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=embed)

        except Exception as e:
            logging.error(f"Error al comprar la propiedad: {str(e)}")
            embed = discord.Embed(
                title="¡Compra Fallida!",
                description=f"Ocurrió un error al comprar la propiedad.",
                color=discord.Color.red(),
                timestamp=ctx.message.created_at
            )
            await ctx.send(embed=embed)

    @commands.command(name='proximos_pagos', help="Mostrar los próximos pagos de renta de las propiedades.")
    async def proximos_pagos(self, ctx):
        await self._get_pagos(ctx)

    # Slash Command
    @app_commands.command(name='proximos_pagos', description='Mostrar los próximos pagos de renta de las propiedades.')
    async def slash_proximos_pagos(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._get_pagos(ctx)

    async def _get_pagos(self, ctx):
        pagos = obtener_pagos()

        # Verifica si obtuviste datos
        if not pagos or len(pagos) == 0:
            await ctx.send("No se encontraron pagos.")
            return

        # Obtener el primer pago (el primer usuario)
        primer_pago = pagos[0]

        # Función para convertir la hora UTC a la hora de Chile
        def convertir_a_hora_local(hora_utc):
            tz_chile = pytz.timezone('America/Santiago')
            hora_utc = hora_utc.replace(tzinfo=pytz.utc)  # Asegurar que la hora es consciente de UTC
            return hora_utc.astimezone(tz_chile)

        # Formatear las fechas al estilo Hora:Minutos Día/Mes/Año con conversión de zona horaria
        def formatear_fecha(fecha):
            fecha_local = convertir_a_hora_local(fecha)
            return fecha_local.strftime('%H:%M %d/%m/%Y')

        # Obtener las fechas formateadas
        next_desgaste = formatear_fecha(primer_pago['next_desgaste'])
        next_renta = formatear_fecha(primer_pago['next_renta'])
        next_mantenimiento = formatear_fecha(primer_pago['next_mantenimiento'])
        next_costos_diarios = formatear_fecha(primer_pago['next_costos_diarios'])

        bot_avatar_url = ctx.me.avatar.url
        # Crear un embed separado para cada fecha
        embed_desgaste = discord.Embed(
            title=f"Próximo Desgaste",
            description=next_desgaste,
            color=discord.Color.blue(),
            timestamp=convertir_a_hora_local(ctx.message.created_at)  # Convertir la hora de creación a Chile
        )
        embed_desgaste.set_thumbnail(url=bot_avatar_url)

        embed_renta = discord.Embed(
            title=f"Próxima Renta",
            description=next_renta,
            color=discord.Color.green(),
            timestamp=convertir_a_hora_local(ctx.message.created_at)
        )
        embed_renta.set_thumbnail(url=bot_avatar_url)

        embed_mantenimiento = discord.Embed(
            title=f"Próximo Mantenimiento",
            description=next_mantenimiento,
            color=discord.Color.orange(),
            timestamp=convertir_a_hora_local(ctx.message.created_at)
        )
        embed_mantenimiento.set_thumbnail(url=bot_avatar_url)

        embed_costos_diarios = discord.Embed(
            title=f"Próximos Costos Diarios",
            description=next_costos_diarios,
            color=discord.Color.red(),
            timestamp=convertir_a_hora_local(ctx.message.created_at)
        )
        embed_costos_diarios.set_thumbnail(url=bot_avatar_url)

        # Enviar los embeds individualmente
        await ctx.send(embed=embed_desgaste)
        await ctx.send(embed=embed_renta)
        await ctx.send(embed=embed_mantenimiento)
        await ctx.send(embed=embed_costos_diarios)

    # Comando: !ver_propiedad_hogar
    @commands.command(name='ver_propiedad_hogar', help='Muestra una propiedad tipo hogar disponible en el mercado.')
    async def ver_propiedad_hogar(self, ctx):
        await self._ver_propiedad_hogar(ctx)

    # Slash Command
    @app_commands.command(name='ver_propiedad_hogar', description='Muestra una propiedad tipo hogar disponible en el mercado')
    async def slash_ver_propiedad_hogar(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._ver_propiedad_hogar(ctx)

    async def _ver_propiedad_hogar(self, ctx):
        propiedad = generar_propiedad('hogar')
        self.ultima_propiedad_generada = propiedad

        embed = discord.Embed(
            title="Propiedad Hogar en Venta",
            description=f"**{propiedad['nombre']}** está disponible para compra.",
            color=discord.Color.from_str(propiedad['color'])
        )

        embed.add_field(name="Valor de Compra", value=f"${int(propiedad['valor_compra']):,}".replace(",", "."), inline=False)
        embed.add_field(name="Renta Diaria", value=f"${int(propiedad['renta_diaria']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Costo Diario", value=f"${int(propiedad['costo_diario']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Costo Mantenimiento", value=f"${int(propiedad['costo_mantenimiento']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Nivel", value=f"{propiedad['nivel']}", inline=True)
        embed.add_field(name="Tier", value=f"{propiedad['tier']}", inline=True)
        embed.add_field(name="Barrio", value=f"{propiedad['barrio']}", inline=True)
        embed.add_field(name="Tamaño", value=f"{propiedad['tamaño']}", inline=True)
        embed.add_field(name="Pisos", value=f"{propiedad['pisos']}", inline=True)
        embed.add_field(name="Desgaste", value=f"{propiedad['desgaste']}", inline=True)
        embed.add_field(name="Suerte", value=f"{propiedad['suerte']}", inline=True)

        await ctx.send(embed=embed)

    # Slash Command

    @app_commands.command(name='ver_propiedad_tienda', description='Muestra una propiedad tipo tienda disponible en el mercado')
    async def slash_ver_propiedad_tienda(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._ver_propiedad_tienda(ctx)

    async def _ver_propiedad_tienda(self, ctx):
        propiedad = generar_propiedad('tienda')
        self.ultima_propiedad_generada = propiedad

        embed = discord.Embed(
            title="Propiedad Tienda en Venta",
            description=f"**{propiedad['nombre']}** está disponible para compra.",
            color=discord.Color.from_str(propiedad['color'])
        )

        embed.add_field(name="Valor de Compra", value=f"${int(propiedad['valor_compra']):,}".replace(",", "."), inline=False)
        embed.add_field(name="Renta Diaria", value=f"${int(propiedad['renta_diaria']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Costo Diario", value=f"${int(propiedad['costo_diario']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Costo Mantenimiento", value=f"${int(propiedad['costo_mantenimiento']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Nivel", value=f"{propiedad['nivel']}", inline=True)
        embed.add_field(name="Tier", value=f"{propiedad['tier']}", inline=True)
        embed.add_field(name="Barrio", value=f"{propiedad['barrio']}", inline=True)
        embed.add_field(name="Tamaño", value=f"{propiedad['tamaño']}", inline=True)
        embed.add_field(name="Pisos", value=f"{propiedad['pisos']}", inline=True)
        embed.add_field(name="Desgaste", value=f"{propiedad['desgaste']}", inline=True)
        embed.add_field(name="Suerte", value=f"{propiedad['suerte']}", inline=True)

        await ctx.send(embed=embed)

    # Comando: !ver_propiedad_tienda renta:value

        # Comando: !ver_propiedad_hogar

    @commands.command(name='ver_propiedad_tienda_con_renta', help='Muestra una propiedad tipo tienda disponible en el mercado. ')
    async def ver_propiedad_tienda_con_renta(self, ctx, renta: int):
        await self._ver_propiedad_tienda_con_renta(ctx, renta)

    # Slash Command
    @app_commands.command(name='ver_propiedad_tienda_con_renta', description='Muestra una propiedad tipo tienda disponible en el mercado')
    async def slash_ver_propiedad_tienda_con_renta(self, interaction: discord.Interaction, renta: int):
        ctx = await commands.Context.from_interaction(interaction)
        await self._ver_propiedad_tienda_con_renta(ctx, renta)

    async def _ver_propiedad_tienda_con_renta(self, ctx, renta: int):
        propiedad = generar_propiedad('tienda')
        ultima_propiedad_generada = propiedad  # Asignar valor antes del ciclo
        while propiedad['renta_diaria'] < renta:
            propiedad = generar_propiedad('tienda')
            ultima_propiedad_generada = propiedad  # Actualizar en cada iteración

        embed = discord.Embed(
            title="Propiedad Tienda en Venta",
            description=f"**{propiedad['nombre']}** está disponible para compra.",
            color=discord.Color.from_str(propiedad['color'])
        )
        embed.add_field(name="Valor de Compra", value=f"${int(ultima_propiedad_generada['valor_compra']):,}".replace(",", "."), inline=False)
        embed.add_field(name="Renta Diaria", value=f"${int(ultima_propiedad_generada['renta_diaria']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Costo Diario", value=f"${int(ultima_propiedad_generada['costo_diario']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Costo Mantenimiento", value=f"${int(ultima_propiedad_generada['costo_mantenimiento']):,}".replace(",", "."), inline=True)
        embed.add_field(name="Nivel", value=f"{ultima_propiedad_generada['nivel']}", inline=True)
        embed.add_field(name="Tier", value=f"{ultima_propiedad_generada['tier']}", inline=True)
        embed.add_field(name="Barrio", value=f"{ultima_propiedad_generada['barrio']}", inline=True)
        embed.add_field(name="Tamaño", value=f"{ultima_propiedad_generada['tamaño']}", inline=True)
        embed.add_field(name="Pisos", value=f"{ultima_propiedad_generada['pisos']}", inline=True)
        embed.add_field(name="Desgaste", value=f"{ultima_propiedad_generada['desgaste']}", inline=True)
        embed.add_field(name="Suerte", value=f"{ultima_propiedad_generada['suerte']}", inline=True)
        await ctx.send(embed=embed)

    # Comando: !comprar_propiedad_generada

    @commands.command(name='comprar_propiedad_generada', help='Compra la última propiedad generada en el mercado. Uso: !comprar_propiedad_generada')
    async def comprar_propiedad_generada(self, ctx):
        await self._comprar_propiedad_generada(ctx)

    # Slash Command
    @app_commands.command(name='comprar_propiedad_generada', description='Compra la última propiedad generada en el mercado')
    async def slash_comprar_propiedad_generada(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._comprar_propiedad_generada(ctx)

    async def _comprar_propiedad_generada(self, ctx):
        if not self.ultima_propiedad_generada:
            embed = discord.Embed(
                title="Error",
                description="No hay ninguna propiedad generada. Usa /ver_propiedad_hogar o /ver_propiedad_tienda primero.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        if not es_inversionista(usuario_id, guild_id):
            embed = discord.Embed(
                title="Error",
                description="No estás registrado como inversionista. Usa **/registrar_inversionista** para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        id_inversionista = obtener_id_inversionista(usuario_id, guild_id)
        propiedad = self.ultima_propiedad_generada
        propiedad['usuario_id'] = id_inversionista

        try:
            comprar_propiedad(usuario_id, guild_id, propiedad)
            valor_compra_formateado = f"${int(propiedad['valor_compra']):,}".replace(",", ".")
            embed = discord.Embed(
                title="¡Compra Exitosa!",
                description=f"Has comprado la propiedad: **{propiedad['nombre']}**.",
                color=discord.Color.green()
            )
            embed.add_field(name="Valor de Compra", value=valor_compra_formateado, inline=False)
            await ctx.send(embed=embed)
            self.ultima_propiedad_generada = None
        except Exception as e:
            logging.error(f"Error al comprar la propiedad: {str(e)}")
            embed = discord.Embed(
                title="¡Compra Fallida!",
                description=f"Ocurrió un error al comprar la propiedad.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !vender_propiedad [propiedad_id]
    @commands.command(name='vender_propiedad', help='Vende una propiedad específica y recibe dinero según su valor.')
    async def vender_propiedad(self, ctx, propiedad_id: int):
        await self._vender_propiedad(ctx, propiedad_id)

    # Slash Command
    @app_commands.command(name='vender_propiedad', description='Vende una propiedad específica y recibe dinero según su valor')
    async def slash_vender_propiedad(self, interaction: discord.Interaction, propiedad_id: int):
        ctx = await commands.Context.from_interaction(interaction)
        await self._vender_propiedad(ctx, propiedad_id)

    async def _vender_propiedad(self, ctx, propiedad_id: int):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        id_inversionista = obtener_id_inversionista(usuario_id, guild_id)
        saldo_nuevo = vender_propiedad(id_inversionista, usuario_id, guild_id, propiedad_id)
        if saldo_nuevo:
            embed = discord.Embed(
                title="¡Venta Exitosa!",
                description=f"Has vendido la propiedad {propiedad_id}. Tu nuevo saldo es {saldo_nuevo}.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="¡Venta Fallida!",
                description="Ocurrió un error al vender la propiedad.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !global_event
    @commands.command(name='global_event', help='Ejecuta un evento global que afecta a todas las rentas.')
    async def global_event(self, ctx):
        await self._global_event(ctx)

    # Slash Command
    @app_commands.command(name='global_event', description='Ejecuta un evento global que afecta a todas las rentas')
    async def slash_global_event(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._global_event(ctx)

    async def _global_event(self, ctx):
        event = obtener_evento_global()
        if event:
            await ctx.send(f"El evento actual es {event}")
        else:
            await ctx.send("No hay ningún evento actualmente.")

    # Comando: !listar_propiedades
    @commands.command(name='listar_propiedades', help='Lista todas tus propiedades.')
    async def listar_propiedades(self, ctx):
        await self._listar_propiedades(ctx)

    # Slash Command
    @app_commands.command(name='listar_propiedades', description='Lista todas tus propiedades')
    async def slash_listar_propiedades(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._listar_propiedades(ctx)

    async def _listar_propiedades(self, ctx):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        inversionista_id = obtener_id_inversionista(usuario_id, guild_id)
        propiedades = obtener_propiedades_por_usuario(inversionista_id)

        if not propiedades:
            await ctx.send("No tienes propiedades.")
            return

        for propiedad in propiedades:
            embed = discord.Embed(
                title=f"Propiedad: {propiedad['nombre']}",
                description=f"Pequeña descripción de la propiedad.",
                color=discord.Color.from_str(propiedad['color'])
            )

            embed.add_field(name="ID", value=f"{propiedad['id']}", inline=True)
            embed.add_field(name="Renta Diaria", value=f"${int(propiedad['renta_diaria']):,}".replace(",", "."), inline=True)
            embed.add_field(name="Costo Diario", value=f"${int(propiedad['costo_diario']):,}".replace(",", "."), inline=True)

            embed.set_footer(text=f"Propiedad en el barrio {propiedad['barrio']} | Costo Mantenimiento: ${int(propiedad['costo_mantenimiento']):,}. | Nivel: {propiedad['nivel']} | Tier: {propiedad['tier']} | Suerte: {propiedad['suerte']} | Desgaste: {propiedad['desgaste']}")

            await ctx.send(embed=embed)

    # Comando: !detalles_propiedad
    @commands.command(name='detalles_propiedad', help='Muestra los detalles de una propiedad específica.')
    async def detalles_propiedad(self, ctx, propiedad_id: int):
        await self._detalles_propiedad(ctx, propiedad_id)

    # Slash Command
    @app_commands.command(name='detalles_propiedad', description='Muestra los detalles de una propiedad específica')
    async def slash_detalles_propiedad(self, interaction: discord.Interaction, propiedad_id: int):
        ctx = await commands.Context.from_interaction(interaction)
        await self._detalles_propiedad(ctx, propiedad_id)

    async def _detalles_propiedad(self, ctx, propiedad_id: int):
        propiedad = obtener_propiedad(propiedad_id)
        if propiedad:
            embed = discord.Embed(
                title=f"Detalles de la Propiedad: {propiedad['nombre']}",
                color=discord.Color.from_str(propiedad['color'])
            )

            embed.add_field(name="Tipo", value=propiedad['tipo'], inline=True)
            embed.add_field(name="Barrio", value=f"{propiedad['barrio']}", inline=True)
            embed.add_field(name="Nivel", value=f"{propiedad['nivel']}", inline=True)
            embed.add_field(name="Tier", value=f"{propiedad['tier']}", inline=True)
            embed.add_field(name="Renta Diaria", value=f"${int(propiedad['renta_diaria']):,}".replace(",", "."), inline=True)
            embed.add_field(name="Costo Diario", value=f"${int(propiedad['costo_diario']):,}".replace(",", "."), inline=True)
            embed.add_field(name="Costo Mantenimiento", value=f"${int(propiedad['costo_mantenimiento']):,}".replace(",", "."), inline=True)
            embed.add_field(name="Suerte", value=f"{propiedad['suerte']}", inline=True)

            embed.set_footer(text=f"Valor de compra: ${int(propiedad['valor_compra']):,} | Tamaño: {propiedad['tamaño']}m² | Piso/s: {propiedad['pisos']} | Desgaste: {propiedad['desgaste']} | Arrendada: {'Sí' if propiedad['arrendada'] else 'No'} | Residencia Principal: {'Sí' if propiedad['es_residencia_principal'] else 'No'}")

            await ctx.send(embed=embed)
        else:
            await ctx.send("No se encontró la propiedad.")

    # Comando: !mejorar_propiedad
    @commands.command(name='mejorar_propiedad', help='Mejora el desgaste de una propiedad pagando una cantidad. Uso: !mejorar_propiedad [propiedad_id] [cantidad_pago]')
    async def mejorar_propiedad(self, ctx, propiedad_id: int, cantidad_pago: int):
        await self._mejorar_propiedad(ctx, propiedad_id, cantidad_pago)

    # Slash Command
    @app_commands.command(name='mejorar_propiedad', description='Mejora el desgaste de una propiedad pagando una cantidad')
    async def slash_mejorar_propiedad(self, interaction: discord.Interaction, propiedad_id: int, cantidad_pago: int):
        ctx = await commands.Context.from_interaction(interaction)
        await self._mejorar_propiedad(ctx, propiedad_id, cantidad_pago)

    async def _mejorar_propiedad(self, ctx, propiedad_id: int, cantidad_pago: int):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)
        inversionista_id = obtener_id_inversionista(usuario_id, guild_id)
        propiedad = obtener_propiedad(propiedad_id)

        if not propiedad:
            await ctx.send(f"No se encontró la propiedad con ID {propiedad_id}.")
            return

        if propiedad['inversionista_id'] != inversionista_id:
            await ctx.send("No tienes permisos para mejorar esta propiedad.")
            return

        if cantidad_pago <= 0:
            await ctx.send("La cantidad de MelladoCoins debe ser positiva.")
            return

        try:
            mejorar_desgaste(propiedad_id, cantidad_pago)
            embed = discord.Embed(
                title="¡Mejora Exitosa!",
                description=f"El desgaste de la propiedad con ID {propiedad_id} ha sido mejorado.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error al mejorar la propiedad: {str(e)}")
            embed = discord.Embed(
                title="¡Mejora Fallida!",
                description=f"Ocurrió un error al mejorar la propiedad.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !estado_inversionista
    @commands.command(name='estado_inversionista', help='Muestra el estado actual del inversionista.')
    async def estado_inversionista(self, ctx):
        await self._estado_inversionista(ctx)

    # Slash Command
    @app_commands.command(name='estado_inversionista', description='Muestra el estado actual del inversionista')
    async def slash_estado_inversionista(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._estado_inversionista(ctx)

    async def _estado_inversionista(self, ctx):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        if not es_inversionista(usuario_id, guild_id):
            embed = discord.Embed(
                title="Error",
                description="No estás registrado como inversionista. Usa **/registrar_inversionista** para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        id_inversionista = obtener_id_inversionista(usuario_id, guild_id)

        try:
            estado = verificar_estado_inversionista(id_inversionista)
            saldo = obtener_saldo_usuario(usuario_id, guild_id)

            if estado is not None:
                saldo_formateado = f"${int(saldo):,}".replace(",", ".")
                embed = discord.Embed(
                    title="Estado del Inversionista",
                    description=f"Estado: Penalizado: {estado}, Saldo: {saldo_formateado} MelladoCoins",
                    color=discord.Color.blue()
                )
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Error",
                    description="No estás registrado como inversionista.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error al obtener el estado del inversionista: {str(e)}")
            embed = discord.Embed(
                title="Error",
                description="Ocurrió un error al obtener el estado del inversionista.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !renta_diaria

    @commands.command(name='renta_diaria', help='Muestra la renta diaria total de tus propiedades.')
    async def renta_diaria(self, ctx):
        await self._renta_diaria(ctx)

    # Slash Command
    @app_commands.command(name='renta_diaria', description='Muestra la renta diaria total de tus propiedades')
    async def slash_renta_diaria(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._renta_diaria(ctx)

    async def _renta_diaria(self, ctx):
        usuario_id = str(ctx.author.id)
        guild = str(ctx.guild.id)

        if not es_inversionista(usuario_id, guild):
            embed = discord.Embed(
                title="Error",
                description="No estás registrado como inversionista.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        id_inversionista = obtener_id_inversionista(usuario_id, guild)
        try:
            propiedades = obtener_propiedades_por_usuario(id_inversionista)
            renta_total = sum([propiedad['renta_diaria'] for propiedad in propiedades])
            renta_total_formateada = f"${int(renta_total):,}".replace(",", ".")
            embed = discord.Embed(
                title="Renta Diaria",
                description=f"Tu renta diaria total es de {renta_total_formateada} MelladoCoins.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error al obtener la renta diaria: {str(e)}")
            embed = discord.Embed(
                title="Error",
                description="Ocurrió un error al obtener la renta diaria.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !costo_diario
    @commands.command(name='costo_diario', help='Muestra el costo diario de todas tus propiedades.')
    async def costo_diario(self, ctx):
        await self._costo_diario(ctx)

    # Slash Command
    @app_commands.command(name='costo_diario', description='Muestra el costo diario de todas tus propiedades')
    async def slash_costo_diario(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._costo_diario(ctx)

    async def _costo_diario(self, ctx):
        usuario_id = str(ctx.author.id)
        guild = str(ctx.guild.id)

        if not es_inversionista(usuario_id, guild):
            embed = discord.Embed(
                title="Error",
                description="No estás registrado como inversionista.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        id_inversionista = obtener_id_inversionista(usuario_id, guild)
        try:
            propiedades = obtener_propiedades_por_usuario(id_inversionista)

            costo_total = sum([propiedad['costo_diario'] for propiedad in propiedades])
            costo_total_formateado = f"${int(costo_total):,}".replace(",", ".")
            embed = discord.Embed(
                title="Costo Diario",
                description=f"Tu costo diario total es de {costo_total_formateado} MelladoCoins.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error al obtener el costo diario: {str(e)}")
            embed = discord.Embed(
                title="Error",
                description="Ocurrió un error al obtener el costo diario.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !eventos_diarios
    @commands.command(name='eventos_diarios', help='Muestra los eventos globales que afectan las rentas diarias.')
    async def eventos_diarios(self, ctx):
        await self._eventos_diarios(ctx)

    # Slash Command
    @app_commands.command(name='eventos_diarios', description='Muestra los eventos globales que afectan las rentas diarias')
    async def slash_eventos_diarios(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._eventos_diarios(ctx)

    async def _eventos_diarios(self, ctx):
        evento = obtener_evento_global()
        if evento:
            embed = discord.Embed(
                title="Evento Global",
                description=f"Evento actual: {evento}",
                color=discord.Color.yellow()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Evento Global",
                description="No hay eventos globales actualmente.",
                color=discord.Color.blue()
            )
            await ctx.send(embed=embed)

    # Comando: !ver_penalizacion
    @commands.command(name='ver_penalizacion', help='Consulta el estado de penalización de un usuario.')
    async def ver_penalizacion(self, ctx, usuario: discord.Member):
        await self._ver_penalizacion(ctx, usuario)

    # Slash Command
    @app_commands.command(name='ver_penalizacion', description='Consulta el estado de penalización de un usuario')
    async def slash_ver_penalizacion(self, interaction: discord.Interaction, usuario: discord.Member):
        ctx = await commands.Context.from_interaction(interaction)
        await self._ver_penalizacion(ctx, usuario)

    async def _ver_penalizacion(self, ctx, usuario: discord.Member):
        usuario_id = str(usuario.id)
        guild_id = str(ctx.guild.id)
        id_inversionista = obtener_id_inversionista(usuario_id, guild_id)

        estado = verificar_estado_inversionista(id_inversionista)

        if estado:
            embed = discord.Embed(
                title="Penalización",
                description=f"El usuario {usuario} con id {id_inversionista} está penalizado.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Penalización",
                description=f"El usuario {usuario} con id {id_inversionista} no está penalizado.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)

    # Comando: !arrendar_propiedad
    @commands.command(name='arrendar_propiedad', help='Arrenda una propiedad tipo hogar. Uso: !arrendar_propiedad [propiedad_id]')
    async def arrendar_propiedad(self, ctx, propiedad_id: int):
        await self._arrendar_propiedad(ctx, propiedad_id)

    # Slash Command
    @app_commands.command(name='arrendar_propiedad', description='Arrenda una propiedad tipo hogar')
    async def slash_arrendar_propiedad(self, interaction: discord.Interaction, propiedad_id: int):
        ctx = await commands.Context.from_interaction(interaction)
        await self._arrendar_propiedad(ctx, propiedad_id)

    async def _arrendar_propiedad(self, ctx, propiedad_id: int):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        if not es_inversionista(usuario_id, guild_id):
            embed = discord.Embed(
                title="Error",
                description="No estás registrado como inversionista. Usa **/registrar_inversionista** para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        id_inversionista = obtener_id_inversionista(usuario_id, guild_id)
        propiedad = obtener_propiedad(propiedad_id)

        if not propiedad:
            embed = discord.Embed(
                title="Error",
                description=f"No se encontró la propiedad con ID {propiedad_id}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if propiedad['inversionista_id'] != id_inversionista:
            embed = discord.Embed(
                title="Error",
                description="No tienes permisos para arrendar esta propiedad.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if propiedad['tipo'] != 'hogar':
            embed = discord.Embed(
                title="Error",
                description="Solo puedes arrendar propiedades de tipo hogar.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if propiedad['es_residencia_principal']:
            propiedades_home = obtener_propiedades_home(id_inversionista)
            if len(propiedades_home) <= 1:
                embed = discord.Embed(
                    title="Error",
                    description="No puedes arrendar tu residencia principal porque no tienes otra propiedad hogar marcada como residencia principal.",
                    color=discord.Color.red()
                )
                await ctx.send(embed=embed)
                return

        if propiedad['arrendada']:
            embed = discord.Embed(
                title="Error",
                description=f"La propiedad {propiedad['nombre']} ya está arrendada.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            actualizar_estado_propiedad_arrendada(propiedad_id, arrendada=True)
            actualizar_estado_residencia_principal(propiedad_id, es_residencia_principal=False)
            embed = discord.Embed(
                title="Arriendo Exitoso",
                description=f"La propiedad {propiedad['nombre']} ha sido arrendada.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error al arrendar la propiedad: {str(e)}")
            embed = discord.Embed(
                title="Error",
                description=f"Ocurrió un error al arrendar la propiedad: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !establecer_residencia_principal
    @commands.command(name='establecer_residencia_principal', help='Establece una propiedad hogar como residencia principal. Uso: !establecer_residencia_principal [propiedad_id]')
    async def establecer_residencia_principal(self, ctx, propiedad_id: int):
        await self._establecer_residencia_principal(ctx, propiedad_id)

    # Slash Command
    @app_commands.command(name='establecer_residencia_principal', description='Establece una propiedad hogar como residencia principal')
    async def slash_establecer_residencia_principal(self, interaction: discord.Interaction, propiedad_id: int):
        ctx = await commands.Context.from_interaction(interaction)
        await self._establecer_residencia_principal(ctx, propiedad_id)

    async def _establecer_residencia_principal(self, ctx, propiedad_id: int):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        if not es_inversionista(usuario_id, guild_id):
            embed = discord.Embed(
                title="Error",
                description="No estás registrado como inversionista. Usa **/registrar_inversionista** para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        id_inversionista = obtener_id_inversionista(usuario_id, guild_id)
        propiedad = obtener_propiedad(propiedad_id)

        if not propiedad:
            embed = discord.Embed(
                title="Error",
                description=f"No se encontró la propiedad con ID {propiedad_id}.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if propiedad['inversionista_id'] != id_inversionista:
            embed = discord.Embed(
                title="Error",
                description="No tienes permisos para modificar esta propiedad.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if propiedad['tipo'] != 'hogar':
            embed = discord.Embed(
                title="Error",
                description="Solo puedes establecer propiedades de tipo hogar como residencia principal.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        try:
            if propiedad['arrendada']:
                actualizar_estado_propiedad_arrendada(propiedad_id, arrendada=False)

            propiedades_home = obtener_propiedades_por_usuario(usuario_id)
            for prop in propiedades_home:
                if prop['tipo'] == 'hogar' and prop['es_residencia_principal']:
                    actualizar_estado_residencia_principal(prop['id'], es_residencia_principal=False)

            actualizar_estado_residencia_principal(propiedad_id, es_residencia_principal=True)
            embed = discord.Embed(
                title="Residencia Principal",
                description=f"La propiedad {propiedad['nombre']} ha sido establecida como residencia principal.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logging.error(f"Error al establecer la residencia principal: {str(e)}")
            embed = discord.Embed(
                title="Error",
                description="Ocurrió un error al establecer la residencia principal",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    # Comando: !home
    @commands.command(name='home', help='Lista todas tus propiedades tipo hogar que son tu residencia principal.')
    async def home(self, ctx):
        await self._home(ctx)

    # Slash Command
    @app_commands.command(name='home', description='Lista todas tus propiedades tipo hogar que son tu residencia principal')
    async def slash_home(self, interaction: discord.Interaction):
        ctx = await commands.Context.from_interaction(interaction)
        await self._home(ctx)

    async def _home(self, ctx):
        usuario_id = str(ctx.author.id)
        guild_id = str(ctx.guild.id)

        if not es_inversionista(usuario_id, guild_id):
            embed = discord.Embed(
                title="Error",
                description="No estás registrado como inversionista. Usa **/registrar_inversionista** para registrarte.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        id_inversionista = obtener_id_inversionista(usuario_id, guild_id)
        propiedades_home = obtener_propiedades_home(id_inversionista)

        if not propiedades_home:
            embed = discord.Embed(
                title="Error",
                description="No tienes ninguna propiedad marcada como residencia principal.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Crear un embed para mostrar la información de las propiedades hogar
        embed = discord.Embed(
            title="Tus Propiedades Hogar",
            description="Aquí están todas tus propiedades hogar marcadas como residencia principal.",
            color=discord.Color.blue()
        )

        # Agregar cada propiedad al embed
        for propiedad in propiedades_home:
            embed.add_field(
                name=f"{propiedad['nombre']} (ID: {propiedad['id']})",
                value=f"Renta Diaria: ${int(propiedad['renta_diaria']):,} | Costo Diario: ${int(propiedad['costo_diario']):,} | Costo Mantenimiento: ${int(propiedad['costo_mantenimiento']):,}",
                inline=False
            )

        # Enviar el embed al canal
        await ctx.send(embed=embed)

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
    @tasks.loop(hours=1)
    async def aplicar_desgaste(self):
        logging.info("Iniciando la verificación para aplicar desgaste.")

        # Obtener usuarios que tienen el próximo desgaste programado antes de la fecha actual
        usuarios = obtener_usuarios_con_fecha('next_desgaste', datetime.now())

        if not usuarios:
            logging.info("No se encontraron usuarios para aplicar desgaste.")
            return

        notificaciones_guild = {}

        for usuario in usuarios:
            usuario_id = usuario['usuario_id']
            id = usuario['id']
            user = get_user_inversionista(usuario_id)
            propiedades = obtener_propiedades_por_usuario(usuario['id'])
            guild_id = user['guild_id']
            user_id = user['user_id']

            for propiedad in propiedades:
                nuevo_desaste = aplicar_desgaste_automatico(propiedad)
                actualizar_desgaste_propiedad(propiedad['id'], nuevo_desaste, propiedad['desgaste_minimo'])
                logging.info(f"Desgaste aplicado a la propiedad {propiedad['nombre']} del usuario {usuario['usuario_id']}.")

            # Actualizamos la fecha del próximo desgaste para 7 días después
            nueva_fecha = datetime.now() + timedelta(days=7)
            actualizar_fecha_tarea('next_desgaste', usuario['usuario_id'], nueva_fecha)

            # Acumulamos notificaciones por guild
            if guild_id not in notificaciones_guild:
                notificaciones_guild[guild_id] = []
            notificaciones_guild[guild_id].append(user_id)

        # Notificación de rentas pagadas por cada guild
        for guild in self.bot.guilds:
            if str(guild.id) in notificaciones_guild:
                await self.enviar_notificacion(guild.id, "¡Se han pagado las rentas diarias de todas las propiedades!")
                logging.info(f"Notificación de pago de rentas enviada al servidor {guild.name}.")

    # Pago de renta diaria cada 24 horas

    @tasks.loop(hours=1)
    async def pago_renta_diaria(self):
        logging.info("Iniciando la verificación para el pago de renta diaria.")

        # Obtener inversionistas que tienen la próxima renta programada antes de la fecha actual
        inversionistas = obtener_usuarios_con_fecha('next_renta', datetime.now())

        if not inversionistas:
            logging.info("No se encontraron inversionistas registrados para pagar renta diaria.")
            return

        # Para guardar las notificaciones de cada guild
        notificaciones_guild = {}

        for inversionista in inversionistas:
            usuario_id = inversionista['usuario_id']
            id = inversionista['id']
            user = get_user_inversionista(usuario_id)  # Consulta para obtener los datos del usuario desde 'users'
            guild_id = user['guild_id']  # Ahora obtenemos el guild_id desde la tabla 'users'
            user_id = user['user_id']

            pagar_renta_diaria(id, guild_id, user_id)
            logging.info(f"Renta diaria pagada el inversionista {id} en el servidor {guild_id}.")

            # Actualizamos la fecha de la próxima renta para el día siguiente
            nueva_fecha = datetime.now() + timedelta(days=1)
            actualizar_fecha_tarea('next_renta', usuario_id, nueva_fecha)

            # Acumulamos notificaciones por guild
            if guild_id not in notificaciones_guild:
                notificaciones_guild[guild_id] = []
            notificaciones_guild[guild_id].append(user_id)

        # Notificación de rentas pagadas por cada guild
        for guild in self.bot.guilds:
            if str(guild.id) in notificaciones_guild:
                await self.enviar_notificacion(guild.id, "¡Se han pagado las rentas diarias de todas las propiedades!")
                logging.info(f"Notificación de pago de rentas enviada al servidor {guild.name}.")

    # Pago de mantenimiento cada 3 días
    @tasks.loop(hours=1)  # Verificamos cada hora
    async def pago_mantenimiento(self):
        logging.info("Iniciando la verificación para el pago de mantenimiento.")

        # Obtener inversionistas que tienen el próximo mantenimiento programado antes de la fecha actual
        inversionistas = obtener_usuarios_con_fecha('next_mantenimiento', datetime.now())

        if not inversionistas:
            logging.info("No se encontraron inversionistas para pagar el mantenimiento.")
            return

        # Diccionario para agrupar las notificaciones por guild
        notificaciones_guild = {}

        for inversionista in inversionistas:
            usuario_id = inversionista['usuario_id']
            id = inversionista['id']
            user = get_user_inversionista(usuario_id)  # Consulta a la tabla 'users' para obtener guild_id
            guild_id = user['guild_id']  # Obtenemos el guild_id desde la tabla 'users'
            user_id = user['user_id']

            # Pago del mantenimiento
            pagar_costo_mantenimiento(id, guild_id, user_id)
            logging.info(f"Pago de mantenimiento realizado para el inversionista {id} en el servidor {guild_id}.")

            # Actualizamos la fecha del próximo mantenimiento para 3 días después
            nueva_fecha = datetime.now() + timedelta(days=3)
            actualizar_fecha_tarea('next_mantenimiento', usuario_id, nueva_fecha)

            # Acumulamos notificaciones por guild
            if guild_id not in notificaciones_guild:
                notificaciones_guild[guild_id] = []
            notificaciones_guild[guild_id].append(user_id)

        # Enviar una notificación por cada guild
        for guild in self.bot.guilds:
            if str(guild.id) in notificaciones_guild:
                await self.enviar_notificacion(guild.id, "¡Se ha pagado el costo de mantenimiento de las propiedades!")
                logging.info(f"Notificación de pago de mantenimiento enviada al servidor {guild.name}.")

    # Cobro de costos diarios cada día

    @tasks.loop(hours=24)  # Cada día
    async def pago_diario(self):
        logging.info("Iniciando la tarea de cobro de costos diarios.")

        # Obtener inversionistas que tienen el próximo cobro de costos diarios programado antes de la fecha actual
        inversionistas = obtener_usuarios_con_fecha('next_costos_diarios', datetime.now())

        if not inversionistas:
            logging.info("No se encontraron inversionistas para cobrar los costos diarios.")
            return

        # Diccionario para agrupar las notificaciones por guild
        notificaciones_guild = {}

        # Cobrar el costo diario a cada inversionista
        for inversionista in inversionistas:
            usuario_id = inversionista['usuario_id']
            id = inversionista['id']
            user = get_user_inversionista(usuario_id)  # Consulta para obtener el 'guild_id'
            guild_id = user['guild_id']  # Obtenemos el 'guild_id' desde la tabla 'users'
            user_id = user['user_id']

            # Cobrar el costo diario
            pagar_costo_diario(id, guild_id, user_id)
            logging.info(f"Costo diario cobrado al inversionista  {id} en el servidor {guild_id}.")

            # Actualizamos la fecha del próximo cobro de costos diarios para el día siguiente
            nueva_fecha = datetime.now() + timedelta(days=1)
            actualizar_fecha_tarea('next_costos_diarios', usuario_id, nueva_fecha)

            # Acumulamos notificaciones por guild
            if guild_id not in notificaciones_guild:
                notificaciones_guild[guild_id] = []
            notificaciones_guild[guild_id].append(user_id)

        # Notificación de costos diarios cobrados por cada guild
        for guild in self.bot.guilds:
            if str(guild.id) in notificaciones_guild:
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
