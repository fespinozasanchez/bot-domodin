from riot.models.match.objetive import Objective


class Objectives:
    def __init__(self, baron: Objective, champion: Objective, dragon: Objective, horde: Objective, inhibitor: Objective, rift_herald: Objective, tower: Objective):
        self.baron: Objective = baron
        self.champion: Objective = champion
        self.dragon: Objective = dragon
        self.horde: Objective = horde
        self.inhibitor: Objective = inhibitor
        self.rift_herald: Objective = rift_herald
        self.tower: Objective = tower

    def __repr__(self) -> str:
        return "<Objectives>"

    def __str__(self) -> str:
        return (f"Objectives(Baron={self.baron}, Champion={self.champion}, Dragon={self.dragon}, "
                f"Horde={self.horde}, Inhibitor={self.inhibitor}, RiftHerald={self.rift_herald}, Tower={self.tower})")
