from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from ..base import Base


class ChannelEmoji(Base):

    __tablename__ = 'channel_emojis'

    emoji_id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey("channels.channel_id"), nullable=False)
    channel = relationship("Channel")
    emoji = Column(String(50))
    default_emoji = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Channel Emoji emoji='{self.emoji}'>"
