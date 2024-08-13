from bs4 import BeautifulSoup
import requests
import discord
from discord.ext import commands

def register_commands(bot):
    @bot.command(help="Mira todos los eventos de las ligas mundiales de fútbol")
    async def copita(ctx, msg: str):
        if msg == "chile" or msg == "1":
            await ctx.send("Estos son los eventos de la Chilean Premier League:")
            embed = discord.Embed(
                title="La fabulosa Chilean Premier League",
                description="Estos son los eventos de la Chilean Premier League:",
                color=0xFF5733
            )
            embed.set_author(name="Chilean Premier League")
            events = get_copa(1)

        elif msg == "premier" or msg == "2":
            await ctx.send("Estos son los eventos de la premier league:")
            embed = discord.Embed(
                title="Premier",
                description="Estos son los eventos de la premier league:",
                color=0xFF5733
            )
            embed.set_author(name="English Premier League")
            events = get_copa(2)

        elif msg == "española" or msg == "3":
            await ctx.send("Estos son los eventos de la liga:")
            embed = discord.Embed(
                title="Premier",
                description="Estos son los eventos de La Liga:",
                color=0xFF5733
            )
            embed.set_author(name="Espanish La Liga")
            events = get_copa(3)

        elif msg == "italiana" or msg == "4":
            await ctx.send("Estos son los eventos de la liga Italiana:")
            embed = discord.Embed(
                title="Premier",
                description="Estos son los eventos de la liga Italiana:",
                color=0xFF5733
            )
            embed.set_author(name="Italian Serie A")
            events = get_copa(4)

        elif msg == "alemana" or msg == "5":
            await ctx.send("Estos son los eventos de la Bundesliga:")
            embed = discord.Embed(
                title="Premier",
                description="Estos son los eventos de la Bundesliga:",
                color=0xFF5733
            )
            embed.set_author(name="German Bundesliga")
            events = get_copa(5)

        elif msg == "francesa" or msg == "6":
            await ctx.send("Estos son los eventos de la Ligue 1:")
            embed = discord.Embed(
                title="Premier",
                description="Estos son los eventos de la Ligue 1:",
                color=0xFF5733
            )
            embed.set_author(name="French Ligue 1")
            events = get_copa(6)
        
        else:
            await ctx.send("Por favor, elige una liga válida.")
            return

        # Añadir los eventos al embed
        for event in events:
            fecha = event['date']
            equipo_local = event['home_team']
            resultado = event['score']
            equipo_visitante = event['away_team']
            # Crear el valor de campo del embed
            field_value = f"{equipo_local} {resultado} {equipo_visitante}"
            if event['match_link']:
                field_value += f"\n[Ver evento]({event['match_link']})"
            # Añadir el campo al embed
            embed.add_field(name=f"{fecha}", value=field_value, inline=True)


        liga_info = {
        "1": ("Chilean Premier League", "https://www.thesportsdb.com/images/media/league/poster/9jnacr1682616899.jpg"),
        "premier": ("English Premier League", "https://www.thesportsdb.com/images/media/league/badge/dsnjpz1679951317.png"),
        "2": ("English Premier League", "https://www.thesportsdb.com/images/media/league/badge/dsnjpz1679951317.png"),
        "española": ("Spanish La Liga", "https://www.thesportsdb.com/images/media/league/badge/ja4it51687628717.png"),
        "3": ("Spanish La Liga", "https://www.thesportsdb.com/images/media/league/badge/ja4it51687628717.png"),
        "italiana": ("Italian Serie A", "https://www.thesportsdb.com/images/media/league/badge/67q3q21679951383.png"),
        "4": ("Italian Serie A", "https://www.thesportsdb.com/images/media/league/badge/67q3q21679951383.png"),
        "alemana": ("German Bundesliga", "https://www.thesportsdb.com/images/media/league/badge/teqh1b1679952008.png"),
        "5": ("German Bundesliga", "https://www.thesportsdb.com/images/media/league/badge/teqh1b1679952008.png"),
        "francesa": ("French Ligue 1", "https://www.thesportsdb.com/images/media/league/badge/zcafvy1719637069.png"),
        "6": ("French Ligue 1", "https://www.thesportsdb.com/images/media/league/badge/zcafvy1719637069.png"),
    }
        # Obtener la información de la liga basada en el número o nombre
        liga, thumbnail_url = liga_info.get(msg, ("French Ligue 1", "https://www.thesportsdb.com/images/media/league/poster/3jojms1718437755.jpg"))

        # Establecer el pie de página y la miniatura
        embed.set_footer(text=liga)
        embed.set_thumbnail(url=thumbnail_url)
        # Enviar el embed
        await ctx.send(embed=embed)


def get_copa(number:int):
    if number == 1:
        url = 'https://www.thesportsdb.com/league/4627-Chile-Primera-Division'
    elif number == 2:
        url = 'https://www.thesportsdb.com/league/4328-English-Premier-League'
    elif number == 3:
        url = 'https://www.thesportsdb.com/league/4335-Spanish-La-Liga'
    elif number == 4:
        url = 'https://www.thesportsdb.com/league/4332-Italian-Serie-A'
    elif number == 5:
        url = 'https://www.thesportsdb.com/league/4331-German-Bundesliga'
    elif number == 6:
        url = 'https://www.thesportsdb.com/league/4334-French-Ligue-1'

    response = requests.get(url)

    # Comprobar si la solicitud fue exitosa (código de estado 200)
    if response.status_code == 200:
        # Parsear el contenido HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Encontrar la sección de próximos eventos
        tables = soup.find_all('table')

        
        # Recorrer cada fila para obtener la información
        results_table = None
        for table in tables:
            if 'Results' in table.text:
                results_table = table
                break
            
        if results_table:
            # Extraer las filas de la tabla
            rows = results_table.find_all('tr')

            # Extraer y mostrar los resultados
            results = []
            for row in rows:
                columns = row.find_all('td')
                if len(columns) >= 2:
                    date = columns[0].text.strip()
                    match_link = columns[0].find('a')['href'] if columns[0].find('a') else None
                    home_team = columns[1].text.strip()
                    score = columns[2].text.strip() if len(columns) > 2 else 'N/A'
                    away_team = columns[3].text.strip() if len(columns) > 3 else 'N/A'

                    results.append({
                    'date': date,
                    'home_team': home_team,
                    'score': score,
                    'away_team': away_team,
                    'match_link': f"https://www.thesportsdb.com{match_link}" if match_link else None
                })
        
    

    else:
        print(f"No se pudo acceder a la página. Código de estado: {response.status_code}")
    return results