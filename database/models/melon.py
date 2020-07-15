from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.types import Date, Integer, String, Text

from ..base import Base


class Melon(Base):

    __tablename__ = 'melons'

    melon_id = Column(Integer, primary_key=True)
    key = Column(String(50))
    value = Column(Text(4294000000))
    uses = Column(Integer)
    creator = Column(Integer)
    created = Column(Date)
    guild_id = Column(Integer, ForeignKey("guilds.guild_id"))
    guild = relationship("Guild")
    tags = relationship("Tag", "melons_tags", backref="Melon")
    category_id = Column(Integer, ForeignKey("categories.category_id"))
    category = relationship("Category")

    def __repr__(self):
        return f"<Melon id='{self.melon_id}' key='{self.key}' uses='{self.uses}'>"

    def get_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "tags": [tag.value for tag in self.tags]
        }
