from enum import Enum
from utils import regex_compile_image_invoke, database_connection
from models import *
from sqlalchemy import update


class QueueStatus(Enum):
    queued = 1
    played = 2
    skipped = 3


class BotStatus(Enum):
    stopped = 1
    paused = 2
    playing = 3
    shuffle = 4

    
class BotCommand(Enum):
    stop = 1
    pause = 2
    play = 3
    shuffle = 4
    resume = 5
    circus = 6


class SongsData:
    def __init__(self, artist, added, file_loc, id_, invoke, name,
                 volume=1.0, skipped=0, shuffled=0, used=0):
        self.artist = artist        # ex: Taylor Swift
        self.added = added
        self.file_loc = file_loc    # ex: /home/python/ionify-rewrite/songs/taytay_22.mp3
        self.id_ = id_
        self.invoke = invoke        # ex: taytay 22
        self.name = name            # ex: 22
        self.skipped = skipped
        self.shuffled = shuffled
        self.used = used
        self.volume = volume

    def __repr__(self):
        return "Song: {}".format(self.name)

class ImagesData:
    def __init__(self, added, file_loc, invoke, used, id_=None):
        self.added = added
        self.file_loc = file_loc
        self.id_ = id_
        self.invoke = invoke
        self.used = used
        self.match = regex_compile_image_invoke(invoke)

    def db_update(self, engine, new_used):
        sql_stmt = update(images).where(images.c.id == self.id_).values(used=new_used)
        with database_connection(engine) as db_c:
            db_c.execute(sql_stmt)

    def db_insert(self, engine):
        sql_stmt = images.insert().values(added=self.added, invoke=self.invoke,
                                          used=self.used, file_loc=self.file_loc)
        with database_connection(engine) as db_c:
            db_c.execute(sql_stmt)

    def __repr__(self):
        return "({0.id_}, {0.invoke}, {0.used})".format(self)

class QueueData:
    def __init__(self, song, queue_status = QueueStatus.queued):
        self.song = song
        self.queue_status = queue_status
        




if __name__ == '__main__':
    from datetime import datetime
    a = ImagesData(id_=1, added=datetime.utcnow(), file_loc="",
                   used=10, invoke="a")
    print(a)
