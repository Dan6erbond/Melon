from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from ..base import Base


class GuildCategory(Base):

    __tablename__ = 'guilds_categories'

    guild_category_id = Column(Integer, primary_key=True)
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"), nullable=False)
    guild = relationship("Guild")
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    category = relationship("category")

    def __repr__(self):
        return f"<Guild Category guild='{self.guild_id}' category='{self.category_id}'>"
