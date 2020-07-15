from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean, Integer, String

from ..base import Base


class Category(Base):

    __tablename__ = 'categories'

    category_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    guilds = relationship("Guild", secondary="guilds_categories", backref="Category")
    melons = relationship("Melon")
    default = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Category id='{self.category_id}' name='{self.name}'>"
