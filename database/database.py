import pathlib

from sqlalchemy import create_engine
from sqlalchemy.orm import backref, relationship, sessionmaker

from .base import Base
from .models import *

path = pathlib.Path(__file__).parent.absolute()
engine = create_engine(f'sqlite:///{path}/database.db')

# Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

if __name__ == "__main__":
    # order is important

    Category.__table__.create(bind=engine)
    Guild.__table__.create(bind=engine)
    GuildCategory.__table__.create(bind=engine)

    Channel.__table__.create(bind=engine)
    ChannelEmoji.__table__.create(bind=engine)

    Melon.__table__.create(bind=engine)
    GuildMelon.__table__.create(bind=engine)
    MelonTag.__table__.create(bind=engine)
    Tag.__table__.create(bind=engine)

    Message.__table__.create(bind=engine)
    ReactionRole.__table__.create(bind=engine)
