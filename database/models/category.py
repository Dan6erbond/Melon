from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from ..base import Base
from .guild_category import GuildCategory


class Category(Base):

    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    categories = relationship("Guild", secondary=GuildCategory, backref="Category")

    def __repr__(self):
        return f"<Category id='{self.category_id}' name='{self.name}'>"
