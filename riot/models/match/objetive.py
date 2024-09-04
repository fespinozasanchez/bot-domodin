class Objective:
    def __init__(self, first: bool, kills: int):
        self.first: bool = first
        self.kills: int = kills

    def __repr__(self) -> str:
        return f"<Objective First={self.first}, Kills={self.kills}>"

    def __str__(self) -> str:
        return f"Objective(First={self.first}, Kills={self.kills})"
