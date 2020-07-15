from sqlalchemy import Column
from sqlalchemy.orm import relationship
<<<<<<< HEAD
from sqlalchemy.types import Integer, String

from ..base import Base
from .guild_category import GuildCategory
=======
from sqlalchemy.types import Boolean, Integer, String

from ..base import Base
>>>>>>> master


class Category(Base):

    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True)
    name = Column(String(50))
<<<<<<< HEAD
    categories = relationship("Guild", secondary=GuildCategory, backref="Category")
=======
    guilds = relationship("Guild", secondary="guilds_categories", backref="Category")
    melons = relationship("Melon")
    default = Column(Boolean, default=False)
>>>>>>> master

    def __repr__(self):
        return f"<Category id='{self.category_id}' name='{self.name}'>"
