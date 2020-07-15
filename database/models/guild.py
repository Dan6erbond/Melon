from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from ..base import Base
<<<<<<< HEAD
from .guild_category import GuildCategory
=======
>>>>>>> master


class Guild(Base):

    __tablename__ = 'guilds'

    guild_id = Column(Integer, primary_key=True)
<<<<<<< HEAD
    categories = relationship("Category", secondary=GuildCategory, backref="Guild")
    melons = relationship("Melon")
=======
    categories = relationship("Category", secondary="guilds_categories", backref="Guild")
    melons = relationship("Melon")
    melon_role = Column(Integer)
>>>>>>> master

    def __repr__(self):
        return f"<Guild id='{self.guild_id}'>"
