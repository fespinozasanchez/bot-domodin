import os

# Obtener configuraciones de la base de datos (pueden estar en el Secret)
DATABASE_CONFIG = {
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'mariadb-services'),
}

# Obtener la URL del API de Riot Games (debe venir del ConfigMap)
URL = os.getenv("URL", "https://americas.api.riotgames.com")
