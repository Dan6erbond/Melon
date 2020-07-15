from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship

from ..base import Base


class Guild(Base):

    __tablename__ = 'guilds'

    guild_id = Column(Integer, primary_key=True)
    categories = relationship("Category", secondary="guilds_categories", backref="Guild")
    melons = relationship("Melon")
    melon_role = Column(Integer)

    def __repr__(self):
        return f"<Guild id='{self.guild_id}'>"
