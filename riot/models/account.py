class Account:
    def __init__(self, puuid: str, gameName: str, tagLine: str):
        self.puuid: str = puuid
        self.gameName: str = gameName
        self.tagLine: str = tagLine

    def __repr__(self) -> str:
        return f"<Account {self.gameName}#{self.tagLine}>"

    def __str__(self) -> str:
        return f"Account(PUUID={self.puuid}, GameName={self.gameName}, TagLine={self.tagLine})"
