from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Integer, String

from ..base import Base
from .melon_tag import MelonTag


class Tag(Base):

    __tablename__ = 'tags'

    tag_id = Column(Integer, primary_key=True)
    melons = relationship("Melon", secondary=MelonTag, backref="Tag")
    value = Column(String(50))

    def __repr__(self):
        return f"<Tag id='{self.tag_id}' value='{self.value}'>"
