from typing import Optional


class LeagueEntry:
    def __init__(self,
                 queueType: str,
                 leaguePoints: int,
                 wins: int,
                 losses: int,
                 veteran: bool,
                 inactive: bool,
                 freshBlood: bool,
                 hotStreak: bool,
                 tier: Optional[str] = "Unranked",
                 rank: Optional[str] = "Unranked",
                 **kwargs):
        self.queueType: str = queueType
        self.tier: str = tier
        self.rank: str = rank
        self.leaguePoints: int = leaguePoints
        self.wins: int = wins
        self.losses: int = losses
        self.veteran: bool = veteran
        self.inactive: bool = inactive
        self.freshBlood: bool = freshBlood
        self.hotStreak: bool = hotStreak

    def __repr__(self):
        return (f"LeagueEntry(Queue={self.queueType}, Tier={self.tier} {self.rank}, "
                f"LP={self.leaguePoints}, Wins={self.wins}, Losses={self.losses})")
