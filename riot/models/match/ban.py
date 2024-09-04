class Ban:
    def __init__(self, champion_id: int, pick_turn: int):
        self.champion_id: int = champion_id
        self.pick_turn: int = pick_turn

    def __repr__(self) -> str:
        return f"<Ban ChampionID={self.champion_id}, PickTurn={self.pick_turn}>"

    def __str__(self) -> str:
        return f"Ban(ChampionID={self.champion_id}, PickTurn={self.pick_turn})"
