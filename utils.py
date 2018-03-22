import re

from discord import opus
from ctypes.util import find_library
from contextlib import contextmanager

CHANNEL_TEST = 383215871860015105

@contextmanager
def database_connection(engine):
    conn = engine.connect()
    yield conn
    conn.close()


def compiled_image_regex(image_text):
    text = ".*?{}.*?".format(image_text)
    regex = re.compile(text)
    return regex


def load_opus_library():
    if opus.is_loaded():
        return True
    try:
        find_library('opus')
        return True
    except Exception as e:
        return False
    return False
