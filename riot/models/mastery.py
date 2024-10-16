from typing import List, Optional
from typing import Dict, List, Optional


from typing import Dict, Optional


class NextSeasonMilestone:
    def __init__(self,
                 requireGradeCounts: Dict[str, int],
                 rewardMarks: int,
                 bonus: bool,
                 totalGamesRequires: int,
                 rewardConfig: Optional[Dict[str, int]] = None):
        self.requireGradeCounts: Dict[str, int] = requireGradeCounts  # Mapea los grados a los requisitos (p. ej., "A-": 1)
        self.rewardMarks: int = rewardMarks  # Número de marcas de recompensa
        self.bonus: bool = bonus  # Indica si hay un bono asociado
        self.totalGamesRequires: int = totalGamesRequires  # Número total de juegos requeridos
        self.rewardConfig: Optional[Dict[str, int]] = rewardConfig  # Configuración adicional relacionada con las recompensas

    def __repr__(self) -> str:
        return f"<NextSeasonMilestone RewardMarks={self.rewardMarks}, Bonus={self.bonus}, RewardConfig={self.rewardConfig}>"

    def __str__(self) -> str:
        return (f"NextSeasonMilestone(RewardMarks={self.rewardMarks}, Bonus={self.bonus}, "
                f"TotalGamesRequires={self.totalGamesRequires}, RequireGradeCounts={self.requireGradeCounts}, "
                f"RewardConfig={self.rewardConfig})")


class ChampionMastery:
    def __init__(self,
                 puuid: str,
                 championId: int,
                 championLevel: int,
                 championPoints: int,
                 lastPlayTime: int,
                 championPointsSinceLastLevel: int,
                 championPointsUntilNextLevel: int,
                 markRequiredForNextLevel: int,
                 tokensEarned: int,
                 championSeasonMilestone: int,
                 milestoneGrades: Optional[List[str]] = None,
                 nextSeasonMilestone: Optional[NextSeasonMilestone] = None):
        self.puuid: str = puuid
        self.championId: int = championId
        self.championLevel: int = championLevel
        self.championPoints: int = championPoints
        self.lastPlayTime: int = lastPlayTime
        self.championPointsSinceLastLevel: int = championPointsSinceLastLevel
        self.championPointsUntilNextLevel: int = championPointsUntilNextLevel
        self.markRequiredForNextLevel: int = markRequiredForNextLevel
        self.tokensEarned: int = tokensEarned
        self.championSeasonMilestone: int = championSeasonMilestone
        self.milestoneGrades: Optional[List[str]] = milestoneGrades if milestoneGrades else []
        self.nextSeasonMilestone: Optional[NextSeasonMilestone] = nextSeasonMilestone

    def __repr__(self) -> str:
        return (f"<ChampionMastery ChampionID={self.championId}, Level={self.championLevel}, "
                f"Points={self.championPoints}, LastPlayTime={self.lastPlayTime}>")

    def __str__(self) -> str:
        return (f"ChampionMastery(PUUID={self.puuid}, ChampionID={self.championId}, Level={self.championLevel}, "
                f"Points={self.championPoints}, LastPlayTime={self.lastPlayTime}, PointsSinceLastLevel={self.championPointsSinceLastLevel}, "
                f"PointsUntilNextLevel={self.championPointsUntilNextLevel}, MarksRequiredForNextLevel={self.markRequiredForNextLevel}, "
                f"TokensEarned={self.tokensEarned}, ChampionSeasonMilestone={self.championSeasonMilestone}, "
                f"MilestoneGrades={self.milestoneGrades}, NextSeasonMilestone={self.nextSeasonMilestone})")
