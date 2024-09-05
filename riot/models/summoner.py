from typing import Optional


class Summoner:
    def __init__(self, id: str, accountId: str, puuid: str, profileIconId: int, revisionDate: int, summonerLevel: int):
        self.id: str = id 
        self.accountId: str = accountId
        self.puuid: str = puuid
        self.profileIconId: int = profileIconId
        self.revisionDate: int = revisionDate
        self.summonerLevel: int = summonerLevel

    def __repr__(self) -> str:
        return f"<Summoner NameID={self.id}, Level={self.summonerLevel}>"

    def __str__(self) -> str:
        return (f"Summoner(ID={self.id}, Level={self.summonerLevel}, "
                f"ProfileIconId={self.profileIconId}, AccountId={self.accountId}, "
                f"PUUID={self.puuid}, LastUpdated={self.revisionDate})")
