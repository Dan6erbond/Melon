from sqlalchemy import Column
from sqlalchemy.orm import relationship
<<<<<<< HEAD
from sqlalchemy.types import Integer
=======
from sqlalchemy.types import Integer, Boolean
>>>>>>> master

from ..base import Base


class Channel(Base):

    __tablename__ = 'channels'

    channel_id = Column(Integer, primary_key=True)
    emojis = relationship("ChannelEmoji")
<<<<<<< HEAD
=======
    poll_channel = Column(Boolean, default=False)
>>>>>>> master

    def __repr__(self):
        return f"<Channel id='{self.channel_id}'>"
