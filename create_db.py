from models import *
from cfg import db_loc

import os
import asyncio
import sqlalchemy

async def create_all_tables(engine):
    try:
        metadata.create_all(engine)
        await asyncio.sleep(1)
        return True
    except Exception as e:
        print(e)
        return False
