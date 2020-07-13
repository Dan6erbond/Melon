from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from ..base import Base


class GuildMelon(Base):

    __tablename__ = 'guilds_melons'

    guild_melon_id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"), nullable=False)
    guild = relationship("Guild")
    melon_id = Column(Integer, ForeignKey("melons.melon_id"), nullable=False)
    melon = relationship("Melon")

    def __repr__(self):
        return f"<Guild Melon guild='{self.guild_id}' melon='{self.melon_id}'>"
