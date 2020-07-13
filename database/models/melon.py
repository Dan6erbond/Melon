from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Date, Integer, String, Text

from ..base import Base
from .guild_melon import GuildMelon


class Melon(Base):

    __tablename__ = 'melons'

    melon_id = Column(Integer, primary_key=True)
    key = Column(String(50))
    value = Column(Text(4294000000))
    uses = Column(Integer)
    creator = Column(Integer)
    created = Column(Date)
    guild_exclusive = Column(Integer)
    guilds = relationship("Guild", secondary=GuildMelon, backref="Melon")
    tags = relationship("MelonTag")
    category_id = Column(Integer, ForeignKey("melon_categories.category_id"), nullable=False)
    category = relationship("MelonCategory")

    def __repr__(self):
        return f"<Melon id='{self.melon_id}' key='{self.key}' uses='{self.uses}'>"
