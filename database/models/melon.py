from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, Integer, String, Text

from ..base import Base


class Melon(Base):

    __tablename__ = 'melons'

    melon_id = Column(Integer, primary_key=True)
    key = Column(String(50))
    value = Column(Text(4294000000))
    uses = Column(Integer, default=0, nullable=False)
    created_by = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"))
    guild = relationship("Guild")
    tags = relationship("Tag", "melons_tags", backref="Melon")
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    category = relationship("Category")

    def __repr__(self):
        return f"<Melon id='{self.melon_id}' key='{self.key}' uses='{self.uses}'>"

    def to_dict(self):
        return {
            "created": self.created_at,
            "creator": self.created_by,
            "id"     : self.melon_id,
            "key"    : self.key,
            "tags"   : [tag.value for tag in self.tags],
            "value"  : self.value
        }
