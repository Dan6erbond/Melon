from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from ..base import Base
from .guild_melon import GuildMelon


class Guild(Base):

    __tablename__ = 'guilds'

    guild_id = Column(Integer, primary_key=True)
    melons = relationship("Melon", secondary=GuildMelon, backref="Guild")

    def __repr__(self):
        return f"<Guild id='{self.guild_id}'>"
