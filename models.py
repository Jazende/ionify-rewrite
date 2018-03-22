from sqlalchemy import Table, Column, MetaData
from sqlalchemy import Integer, String, Float, DateTime

metadata = MetaData()

songs = Table('songs', metadata,
              Column('id', Integer, primary_key=True),
              Column('invoke', String),
              Column('file_loc', String),
              Column('artist', String),
              Column('name', String),
              Column('added', DateTime),
              Column('used', Integer),
              Column('skipped', Integer),
              Column('shuffled', Integer),
              Column('volume', Float),
              )

log = Table('log', metadata,
            Column('id', Integer, primary_key=True),
            Column('message', String),
            Column('author', String),
            Column('timestamp', DateTime),
            )

images = Table('images', metadata,
               Column('id', Integer, primary_key=True),
               Column('invoke', String, unique=True),
               Column('file_loc', String),
               Column('added', DateTime),
               Column('used', Integer),
               )
