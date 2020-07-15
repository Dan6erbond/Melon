from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, Boolean

from ..base import Base


class Channel(Base):

    __tablename__ = 'channels'

    channel_id = Column(Integer, primary_key=True)
    emojis = relationship("ChannelEmoji")
    poll_channel = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Channel id='{self.channel_id}'>"
