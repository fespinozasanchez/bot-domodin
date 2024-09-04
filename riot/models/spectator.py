from typing import List, Dict, Optional


class Perks:
    def __init__(self, perkIds: List[int], perkStyle: int, perkSubStyle: int):
        self.perkIds: List[int] = perkIds
        self.perkStyle: int = perkStyle
        self.perkSubStyle: int = perkSubStyle

    def __repr__(self) -> str:
        return f"<Perks Style={self.perkStyle}, SubStyle={self.perkSubStyle}>"

    def __str__(self) -> str:
        return f"Perks(Style={self.perkStyle}, SubStyle={self.perkSubStyle}, PerkIds={self.perkIds})"


class Participant:
    def __init__(self,
                 puuid: str,
                 teamId: int,
                 spell1Id: int,
                 spell2Id: int,
                 championId: int,
                 profileIconId: int,
                 riotId: str,
                 bot: bool,
                 summonerId: str,
                 gameCustomizationObjects: List[Dict],
                 perks: Dict[str, int]):
        self.puuid: str = puuid
        self.teamId: int = teamId
        self.spell1Id: int = spell1Id
        self.spell2Id: int = spell2Id
        self.championId: int = championId
        self.profileIconId: int = profileIconId
        self.riotId: str = riotId
        self.bot: bool = bot
        self.summonerId: str = summonerId
        self.gameCustomizationObjects: List[Dict] = gameCustomizationObjects
        self.perks: Perks = Perks(**perks)

    def __repr__(self) -> str:
        return f"<Participant RiotID={self.riotId}, ChampionID={self.championId}>"

    def __str__(self) -> str:
        return (f"Participant(RiotID={self.riotId}, ChampionID={self.championId}, TeamID={self.teamId}, "
                f"Spells=({self.spell1Id}, {self.spell2Id}), Perks={self.perks}, Bot={self.bot})")


class BannedChampion:
    def __init__(self, championId: int, teamId: int, pickTurn: int):
        self.championId: int = championId
        self.teamId: int = teamId
        self.pickTurn: int = pickTurn

    def __repr__(self) -> str:
        return f"<BannedChampion ChampionID={self.championId}, TeamID={self.teamId}, PickTurn={self.pickTurn}>"

    def __str__(self) -> str:
        return f"BannedChampion(ChampionID={self.championId}, TeamID={self.teamId}, PickTurn={self.pickTurn})"


class Observer:
    def __init__(self, encryptionKey: str):
        self.encryptionKey: str = encryptionKey

    def __repr__(self) -> str:
        return f"<Observer EncryptionKey={self.encryptionKey}>"

    def __str__(self) -> str:
        return f"Observer(EncryptionKey={self.encryptionKey})"


class CurrentGameInfo:
    def __init__(self,
                 gameId: int,
                 mapId: int,
                 gameMode: str,
                 gameType: str,
                 gameQueueConfigId: int,
                 participants: List[Dict],
                 observers: Dict[str, str],
                 platformId: str,
                 bannedChampions: List[Dict],
                 gameStartTime: int,
                 gameLength: int):
        self.gameId: int = gameId
        self.mapId: int = mapId
        self.gameMode: str = gameMode
        self.gameType: str = gameType
        self.gameQueueConfigId: int = gameQueueConfigId
        self.participants: List[Participant] = [Participant(**p) for p in participants]
        self.observers: Observer = Observer(**observers)
        self.platformId: str = platformId
        self.bannedChampions: List[BannedChampion] = [BannedChampion(**bc) for bc in bannedChampions]
        self.gameStartTime: int = gameStartTime
        self.gameLength: int = gameLength

    def __repr__(self) -> str:
        return f"<CurrentGameInfo GameID={self.gameId}, Mode={self.gameMode}, Length={self.gameLength}>"

    def __str__(self) -> str:
        participants_str = "\n  ".join(str(p) for p in self.participants)
        banned_champions_str = "\n  ".join(str(bc) for bc in self.bannedChampions)
        return (f"CurrentGameInfo(GameID={self.gameId}, Mode={self.gameMode}, Type={self.gameType}, "
                f"MapID={self.mapId}, QueueConfigID={self.gameQueueConfigId}, Length={self.gameLength}, "
                f"PlatformID={self.platformId}, GameStartTime={self.gameStartTime})\n"
                f"Participants:\n  {participants_str}\n"
                f"BannedChampions:\n  {banned_champions_str}\n"
                f"Observers:\n  {self.observers}")


class FeaturedGame(CurrentGameInfo):
    pass
