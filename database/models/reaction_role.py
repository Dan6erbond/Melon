from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from ..base import Base


class ReactionRole(Base):

    __tablename__ = 'reaction_roles'

    reaction_role_id = Column(Integer, primary_key=True)
    role = Column(Integer)
    emoji = Column(String(50))

    def __repr__(self):
        return f"<Reaction Role id='{self.reaction_role_id}' role='{self.role}' emoji='{self.emoji}'>"