from fastapi import FastAPI
from rpg_module.rpg_utils.rpg_data_manager import get_player_by_name, get_all_players




app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/players/{player_name}")
def read_item(player_name:str):
    return {"player_name": get_player_by_name(player_name)}

@app.get("/all_players/")
def all_players():
    return {"players": get_all_players()}


