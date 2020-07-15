from sqlalchemy import Column
from sqlalchemy.orm import relationship
<<<<<<< HEAD
=======
from sqlalchemy.schema import ForeignKey
>>>>>>> master
from sqlalchemy.types import Integer, String

from ..base import Base


class ReactionRole(Base):

    __tablename__ = 'reaction_roles'

    reaction_role_id = Column(Integer, primary_key=True)
<<<<<<< HEAD
    role = Column(Integer)
=======
    message_id = Column(Integer, ForeignKey("messages.message_id"))
    message = relationship("Message")
    role = Column(Integer, nullable=False)
>>>>>>> master
    emoji = Column(String(50))

    def __repr__(self):
        return f"<Reaction Role id='{self.reaction_role_id}' role='{self.role}' emoji='{self.emoji}'>"
