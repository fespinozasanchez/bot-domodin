def handle_api_error(error):
    # Manejo básico de errores de la API
    print(f"Error: {error.response.status_code} - {error.response.text}")


def format_game_data(game_data):
    # Formateo básico de los datos del juego
    return f"Game ID: {game_data['gameId']}, Mode: {game_data['gameMode']}"
