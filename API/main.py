from fastapi import FastAPI, Response, status
from rpg_module.rpg_utils.rpg_data_manager import get_player_by_name, get_all_players
from utils.natural_events_manager import get_current_natural_event
from utils.market_data_manager import get_current_event, obtener_propiedad,obtener_pagos,obtener_propiedades_por_usuario,obtener_propiedades_por_color





app = FastAPI()


@app.get("/")
def root():
    return {"message": "What are you looking for 🙄"}


@app.get("/players/{player_name}")
def read_item(player_name:str, response: Response):
    player=get_player_by_name(player_name)
    if not player:
        response.status_code = status.HTTP_404_NOT_FOUND
    return {"player_name": player}

@app.get("/players/all_players/")
def all_players():
    return {"players": get_all_players()}


@app.get("/natural_events/")
def events():
    return {"events": get_current_natural_event()}

@app.get("/market_data/")
def market_data():
    return {"market_data": get_current_event()}

@app.get("/market_data/{propiedad}")
def propiedad(propiedad:str, response: Response):
    propiedad=obtener_propiedad(propiedad)
    if not propiedad:
        response.status_code = status.HTTP_404_NOT_FOUND
    return {"propiedad":propiedad}

@app.get("/market_data/pagos/")
def pagos():
    return {"pagos": obtener_pagos()}

@app.get("/market_data/propiedades/{inv_id}")
def propiedades(inv_id:str, response: Response):
    propiedades=obtener_propiedades_por_usuario(inv_id)
    if not propiedades:
        response.status_code = status.HTTP_404_NOT_FOUND
    return {"propiedades":propiedades}

@app.get("/market_data/propiedades/color/{color}")
def propiedades_color(color:str, response: Response):
    propiedades=obtener_propiedades_por_color(color)
    if not propiedades:
        response.status_code = status.HTTP_404_NOT_FOUND
    return {"propiedades": propiedades}


