from bs4 import BeautifulSoup
import requests
import discord
from discord.ext import commands


# URL de la página web
def register_commands(bot):
    @bot.command(help="Mira todos los eventos de la copa america")
    async def copita(ctx, msg: str):
        if msg == "america" or msg == "1":
            await ctx.send("Estos son los eventos de la copa america:")
            embed = discord.Embed(
                title="Copa America",
                description="Estos son los eventos de la copa america:",
                color=0xFF5733
            )
            embed.set_author(
                name="Copa America",
                )
            events = get_copa(1)

            for event in events:
                    fecha = event['fecha']
                    equipo_local = event['equipo_local']
                    resultado = event['resultado']
                    equipo_visitante = event['equipo_visitante']
                    embed.add_field(name=f"{fecha}", value=f"{equipo_local} {resultado} {equipo_visitante}", inline=True)
            embed.set_footer(text="Conmmebol Copa America")
            embed.set_thumbnail(
                url="https://www.thesportsdb.com/images/media/league/poster/23s9ii1693644543.jpg")
            await ctx.send(embed=embed)

        elif msg =='europa' or msg == "2":
            await ctx.send("Estos son los eventos de la Eurocopa:")
            embed = discord.Embed(
                title="Euro Copa",
                description="Estos son los eventos de la Eurocopa:",
                color=0xFF5733
            )
            embed.set_author(
                name="UEFA European Championships",
                )
            events = get_copa(2)


            for event in events:
                    fecha = event['fecha']
                    equipo_local = event['equipo_local']
                    resultado = event['resultado']
                    equipo_visitante = event['equipo_visitante']
                    embed.add_field(name=f"{fecha}", value=f"{equipo_local} {resultado} {equipo_visitante}", inline=True)
            embed.set_footer(text="UEFA European Championships")
            embed.set_thumbnail(
                url="https://www.thesportsdb.com/images/media/league/poster/3jojms1718437755.jpg")
            await ctx.send(embed=embed)


    @bot.command(help="Busca un evento de la copa america por fecha")
    async def buscar_evento(ctx, fecha: str):
        events = get_copa(1)
        for event in events:
            if event['fecha'] == fecha:
                await ctx.send(f"{event['fecha']} - {event['equipo_local']} {event['resultado']} {event['equipo_visitante']}")
                return
        await ctx.send(f"No se encontró ningún evento para la fecha {fecha}.")
    


def get_copa(number:int):
    if number == 1:
        url = 'https://www.thesportsdb.com/league/4499-Copa-America'
    elif number == 2:
        url = 'https://www.thesportsdb.com/league/4502-UEFA-European-Championships'  
    response = requests.get(url)

    # Comprobar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Parsear el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar la sección de próximos eventos
        upcoming_events = soup.find('b', string='Upcoming').find_next('table')
        
        # Encontrar las filas de la tabla de próximos eventos
        rows = upcoming_events.find_all('tr')[::-1]
        
        # Variable para controlar la sección actual
        current_section = 'upcoming'  # Puede ser 'upcoming' o 'results'
        
        # Lista para almacenar los eventos
        events_list = []
        
        # Recorrer cada fila para obtener la información
        for row in rows:
            # Verificar si se ha cambiado a la sección de resultados
            if current_section == 'upcoming' and '<b>Results</b>' in str(row):
                current_section = 'results'
                continue  # Saltar esta fila y continuar con la siguiente
            
            # Procesar filas de próximos eventos
            if current_section == 'upcoming':
                cells = row.find_all('td')
                if cells:
                    evento = {
                        'fecha': cells[0].text.strip(),
                        'equipo_local': cells[1].text.strip(),
                        'resultado': cells[2].text.strip(),
                        'equipo_visitante': cells[3].text.strip()
                    }
                    events_list.append(evento)
            
            # Procesar filas de resultados
            elif current_section == 'results':
                cells = row.find_all('td')
                if cells:
                    resultado = {
                        'fecha': cells[0].text.strip(),
                        'equipo_local': cells[1].text.strip(),
                        'resultado': cells[2].text.strip(),
                        'equipo_visitante': cells[3].text.strip()
                    }
                    events_list.append(resultado)
        
    

    else:
        print(f"No se pudo acceder a la página. Código de estado: {response.status_code}")
    return events_list







