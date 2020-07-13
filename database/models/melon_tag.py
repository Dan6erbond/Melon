from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from ..base import Base


class MelonTag(Base):

    __tablename__ = 'melons_tags'

    melon_tag_id = Column(Integer, primary_key=True)
    melon_id = Column(Integer, ForeignKey("melons.melon_id"), nullable=False)
    melon = relationship("Melon")
    tag_id = Column(Integer, ForeignKey("tags.tag_id"), nullable=False)
    tag = relationship("Tag")

    def __repr__(self):
        return f"<Melon Tag melon='{self.melon_id}' tag='{self.tag_id}'>"
