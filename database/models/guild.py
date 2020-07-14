from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from ..base import Base
from .guild_category import GuildCategory


class Guild(Base):

    __tablename__ = 'guilds'

    guild_id = Column(Integer, primary_key=True)
    categories = relationship("Category", secondary=GuildCategory, backref="Guild")
    melons = relationship("Melon")

    def __repr__(self):
        return f"<Guild id='{self.guild_id}'>"
