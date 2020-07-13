from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from ..base import Base


class MelonCategory(Base):

    __tablename__ = 'melon_categories'

    category_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    melons = relationship("Melon")

    def __repr__(self):
        return f"<Category id='{self.category_id}' name='{self.name}'>"
