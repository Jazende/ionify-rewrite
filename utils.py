import os
import re
import aiohttp

from discord import opus
from discord import FFmpegPCMAudio
from statics import BOT_FOLDER_IMAGES
from discord import PCMVolumeTransformer
from contextlib import contextmanager
from ctypes.util import find_library

CHANNEL_TEST = 383215871860015105
REGEX_MATCH_IMAGE_ADD = re.compile("!image add \"(\S[a-zA-Z0-9_]*?\S)\" \"(.*?)\"")
REGEX_FIND_IMAGE_EXT = re.compile(".*\w+/.+\.([\w\d]{1,5})\??.*")


def vol_audio_source(song):
    as_ = FFmpegPCMAudio(song.file_loc)
    vas = PCMVolumeTransformer(as_)
    vas.volume = song.volume
    return vas


def regex_match(regex, input_):
    if re.match(regex, input_):
        return True
    else:
        return False


def regex_findall(regex, input_):
    return re.findall(regex, input_)


@contextmanager
def database_connection(engine):
    conn = engine.connect()
    yield conn
    conn.close()


def regex_compile_image_invoke(image_text):
    text = ".*?{}.*?".format(image_text)
    regex = re.compile(text)
    return regex


def load_opus_library():
    if opus.is_loaded():
        return True
    if find_library('opus'):
        return True
    else:
        return False


async def async_download_picture(name, link):
    ext = regex_findall(REGEX_FIND_IMAGE_EXT, link)
    if not ext:
        return False, "", ""
    picture_name = name+"."+ext[0]
    picture_url = os.path.join(BOT_FOLDER_IMAGES, picture_name)
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as resp:
            with open(picture_url, 'wb') as f:
                f.write(await resp.read())
        await session.close()
    return True, picture_name, picture_url
