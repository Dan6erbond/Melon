import pathlib

from sqlalchemy import create_engine
from sqlalchemy.orm import backref, relationship, sessionmaker

from .base import Base
from .models import *

path = pathlib.Path(__file__).parent.absolute()
engine = create_engine(f'sqlite:///{path}/database.db')

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
