from cfg import db_loc
from utils import compiled_image_regex, database_connection
from models import *
from sqlalchemy import create_engine, update


class SongsData:
    def __init__(self, artist, added, file_loc, id_, invoke, name,
                 skipped=0, shuffled=0, used=0):
        self.artist = artist
        self.added = added
        self.file_loc = file_loc
        self.id_ = id_
        self.invoke = invoke
        self.name = name
        self.skipped = skipped
        self.shuffled = shuffled
        self.used = used

class ImagesData:

    engine = create_engine(db_loc)
    
    def __init__(self, added, file_loc, id_, invoke):
        self.added = added
        self.file_loc = file_loc
        self.id_ = id_
        self.invoke = invoke
        self._used = None
        self.match = compiled_image_regex(invoke)

        @property
        def used(self):
            return self._used

        @used.setter
        def used(self, used):
            try:
                sql_stmt = update(images).where(images.c.id == self.id_).\
                           values(used=used)
                with database_connection(self.engine) as db_c:
                    db_c.execute(sql_stmt)
            except:
                raise Exception("Could not complete")
            else:
                self._used = used

    def __repr__(self):
        return "({0.id_}, {0.invoke}, {0.used})".format(self)

if __name__ == '__main__':
    from datetime import datetime
    a = ImagesData(id_ = 1, added = datetime.utcnow(), file_loc = "",
                   used = 10, invoke = "a")
    print(a)
