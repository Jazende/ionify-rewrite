from models import *
from cfg import db_loc

import os
import sqlalchemy

def create_all_tables(engine):
    try:
        metadata.create_all(engine)
        return True
    except Exception as e:
        print(e)
        return False
