import orjson
import discord

from src.utils.SqlConnector import sql
from datetime import datetime
from src.utils.variousclasses import models, characters


class Guild:
    def __init__(self, id: int):
        self.id = id
        self.load()

    def getDbData(self):
        with sql.mainDb as con:
            curs_data = con.cursor()
            curs_data.execute("SELECT * FROM setup_data WHERE guild_id = ?", (self.id,))
            data = curs_data.fetchone()
        self.isInDb = data is not None
        if not self.isInDb:
            self.updateDbData()
            with sql.mainDb as con:
                curs_data = con.cursor()
                curs_data.execute(
                    "SELECT * FROM setup_data WHERE guild_id = ?", (self.id,)
                )
                data = curs_data.fetchone()
        if type(data[1]) == str and data[1].startswith("b'"):
            data = orjson.loads(data[1][2:-1])
        else:
            data = orjson.loads(data[1])
        self.premium = data["premium"]
        self.channels = data["channels"]
        self.api_keys = data["api_keys"]
        if self.premium:
            self.premium_expiration = datetime.fromisoformat(
                data.get("premium_expiration", None)
            )
            self.checkPremiumExpires()
        else:
            self.premium_expiration = None

    def checkPremiumExpires(self):
        if self.premium_expiration is None:
            self.premium = False
            return
        if self.premium_expiration < datetime.now():
            self.premium = False
            self.premium_expiration = None
            self.updateDbData()

    def updateDbData(self):
        if self.isInDb:
            data = {
                "guild_id": self.id,
                "premium": self.premium,
                "channels": self.channels,
                "api_keys": self.api_keys,
                "premium_expiration": self.premium_expiration.isoformat()
                if self.premium
                else None,
            }
        else:
            data = {
                "guild_id": self.id,
                "premium": False,
                "channels": {},
                "api_keys": {},
                "premium_expiration": None,
            }
        with sql.mainDb as con:
            curs_data = con.cursor()
            if self.isInDb:
                curs_data.execute(
                    "UPDATE setup_data SET guild_settings = ? WHERE guild_id = ?",
                    (orjson.dumps(data), self.id),
                )
            else:
                curs_data.execute(
                    "INSERT INTO setup_data (guild_id, guild_settings) VALUES (?, ?)",
                    (self.id, orjson.dumps(data)),
                )
                self.isInDb = True

    def load(self):
        self.getDbData()

    def addChannel(
        self, channel: discord.TextChannel | str, model: str, character: str
    ):
        if isinstance(channel, discord.TextChannel):
            channel = channel.id
        self.channels[str(channel)] = {
            "model": model,
            "character": character,
        }
        self.updateDbData()

    def delChannel(self, channel: discord.TextChannel | str):
        if isinstance(channel, discord.TextChannel):
            channel = channel.id
        del self.channels[str(channel)]
        self.updateDbData()

    @property
    def sanitizedChannels(self) -> dict:
        if self.premium:
            return self.channels
        if len(self.channels) == 0:
            return {}
        dictionary = {
            list(self.channels.keys())[0]: {
                "model": models.matchingDict[models.default],
                "character": characters.matchingDict[characters.default],
            }
        }
        if self.channels.get("serverwide", None) is not None:
            dictionary["serverwide"] = self.channels["serverwide"]
        return dictionary

    def getChannelInfo(self, channel: str) -> dict:
        return self.sanitizedChannels.get(channel, None)

    def addApiKey(self, api: str, key: str):
        self.api_keys[api] = key
        self.updateDbData()
