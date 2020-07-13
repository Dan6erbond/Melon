from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer

from ..base import Base


class Message(Base):

    __tablename__ = 'messages'

    message_id = Column(Integer, primary_key=True)
    reaction_roles = relationship("ReactionRole")

    def __repr__(self):
        return f"<Message id='{self.message_id}'>"
