from models import *
from statics import *
from dataclasses import *

from cfg import TOKEN, db_loc
from utils import database_connection, CHANNEL_TEST
from utils import REGEX_MATCH_IMAGE_ADD, regex_findall
from utils import async_download_picture
from utils import load_opus_library
from utils import vol_audio_source
from datetime import datetime

import os
import discord
import create_db
import sqlalchemy


def check_database():
    if not os.path.isfile(db_loc):
        engine = sqlalchemy.create_engine(db_loc)
        create_db.create_all_tables(engine)


class Ionify(discord.Client):
    def __init__(self, jaz_debug=False):
        super().__init__()
        self.engine = sqlalchemy.create_engine(db_loc)
        self.sql_select_all_songs = sqlalchemy.sql.select([songs])
        self.image_list = []
        self.populate_image_list()
        self.song_list = []
        self.populate_song_list()
        self.jaz_debug = jaz_debug
        self.vc = None
        self.voice_capable = False
        load_opus_library()

    async def on_ready(self):
        print("Logged in as {0}!".format(self.user))
        if self.jaz_debug:
            await self.change_presence(status=discord.Status.offline)
        voice_channel = self.get_channel(CHANNEL_VOICE)
        if isinstance(voice_channel, discord.VoiceChannel):
            self.vc = await self.get_channel(CHANNEL_VOICE).connect()
            if self.vc:
                self.voice_capable = True
        else:
            raise ValueError("CHANNEL_VOICE is not a VoiceChannel")

    async def on_message(self, message):
        if message.content.startswith("!"):
            
            # logging all commands
            if self.jaz_debug:
                print(PRINT_MESSAGE.format(message))
                log_ins = log.insert().values(author=str(message.author),
                                              message=str(message.content),
                                              timestamp=datetime.utcnow())

                with database_connection(self.engine) as db_c:
                    db_c.execute(log_ins)
            
            if message.content.startswith("!song random"):          # TODO
                await self.song_random(message)
            elif message.content.startswith("!song playing"):          # TODO
                await self.song_playing(message)
            elif message.content.startswith("!song shuffle start"):          # TODO
                await self.song_shuffle_start(message)
            elif message.content.startswith("!song shuffle stop"):          # TODO
                await self.song_shuffle_stop(message)
            elif message.content.startswith("!song skip"):          # TODO
                await self.song_skip(message)
            elif message.content.startswith("!song stop"):          # TODO
                await self.song_stop(message)
            elif message.content.startswith("!song pause"):          # TODO
                await self.song_pause(message)
            elif message.content.startswith("!song resume"):          # TODO
                await self.song_resume(message)
            elif message.content.startswith("!song volume"):          # TODO
                await self.song_volume(message)
            elif message.content.startswith("!song add"):       # <name> <link>          # TODO
                await self.song_add(message)
            elif message.content.startswith("!song queue"):          # TODO
                await self.song_queue(message)
            elif message.content.startswith("!song list update"):          # TODO
                await self.song_list_update(message)
            elif message.content.startswith("!song list"):          # TODO
                await self.songs_list(message)
            elif message.content.startswith("!image add"):      # <name> <link>
                await self.image_add(message)
            elif message.content.startswith("!INSTANT CIRCUS"):          # TODO
                await self.INSTANT_CIRCUS(message)
            elif message.content.startswith("!INSTANT STOP"):          # TODO
                await self.INSTANT_STOP(message)
            elif message.content.startswith("!monika text"):    # <text>          # TODO
                await self.monika_text(message)
            elif message.content.startswith("!monika online"):          # TODO
                await self.monika_online(message)
            elif message.content.startswith("!monika offline"):          # TODO
                await self.monika_offline(message)
            elif message.content.startswith("!monika playing"):          # TODO
                await self.monika_playing(message)
            elif message.content.startswith("!monika commands"):          # TODO
                await self.monika_commands(message)
            elif message.content.startswith("!song "):          # TODO
                await self.play_song(message)
            elif message.content.startswith("!test"):              # todo remove when complete
                await self.test_functionality(message)
        else:
            for image_obj in self.image_list:
                if image_obj.match.match(str(message.content).lower()):
                    if self.jaz_debug:
                        chl = message.channel.guild.get_channel(CHANNEL_TEST)
                        await chl.send(file=discord.File(image_obj.file_loc))
                    else:
                        await message.channel.send(file=discord.File(image_obj.file_loc))
                    image_obj.db_update(self.engine, image_obj.used + 1)

    async def test_functionality(self, message):
        song = os.path.join(BOT_FOLDER_SONGS, 'aqua_barbie_girl.mp3')
        audiosource = discord.FFmpegPCMAudio(song)
        volume_audio = discord.PCMVolumeTransformer(audiosource)
        volume_audio.volume = 2
        self.vc.play(volume_audio, after=lambda e: print('done', e))

    async def song_random(self, message):
        print("Play random song")
        pass

    async def song_playing(self, message):
        print("!song playing")
        pass

    async def song_shuffle_start(self, message):
        print("!song shuffle start")
        pass

    async def song_shuffle_stop(self, message):
        print("!song shuffle stop")
        pass

    async def song_skip(self, message):
        print("!song skip")
        pass
    
    async def song_stop(self, message):
        print("!song stop")
        pass
    
    async def song_pause(self, message):
        print("!song pause")
        pass
    
    async def song_resume(self, message):
        print("!song resume")
        pass
    
    async def song_volume(self, message):
        print("!song volume")
        pass
    
    async def song_add(self, message):
        print("!song add <name> <link>")
        pass
    
    async def song_queue(self, message):
        print("!song queue")
        pass
    
    async def songs_list(self, message):
        print("!song list")
        pass
    
    async def song_list_update(self, message):
        print("!song list update")
        pass
    
    async def image_add(self, message):
        if self.jaz_debug:
            print("!image add <name> <link>")
        matches = regex_findall(REGEX_MATCH_IMAGE_ADD, str(message.content))
        if len(matches) > 0:
            if matches[0] in [x.invoke for x in self.image_list]:
                await message.channel.send("Name already exists. Please pick another.")
            else:
                name, link = matches[0]
                result, pic_name, pic_url = await async_download_picture(name, link)
                if result[0]:
                    new_image = ImagesData(added=datetime.utcnow(), used=0,
                                           file_loc=pic_url, invoke=pic_name)
                    self.image_list.append(new_image)
                    new_image.db_insert(self.engine)
                else:
                    await message.channel.send("Something went wrong downloading the file {}".format(name))

    async def INSTANT_CIRCUS(self, message):
        print("!INSTANT CIRCUS")
        pass
    
    async def INSTANT_STOP(self, message):
        print("!INSTANT STOP")
        pass
    
    async def monika_text(self, message):
        print("!monika text <text>")
        pass
    
    async def monika_online(self, message):
        print("!monika online")
        pass
    
    async def monika_offline(self, message):
        print("!monika offline")
        pass
    
    async def monika_playing(self, message):
        print("!monika playing")
        pass
    
    async def monika_commands(self, message):
        print("!monika commands")
        pass
    
    async def play_song(self, message):
        if self.voice_capable:
            for song in self.song_list:
                if message.content.startswith("!song {}".format(song.invoke)):
                    self.vc.play(vol_audio_source(song), after=lambda e: print("done", e))
        print("!play_song")
        pass

    def populate_image_list(self):
        self.image_list = []
        with database_connection(self.engine) as db_c:
            for image in db_c.execute(sqlalchemy.sql.select([images])):
                self.image_list.append(ImagesData(id_=image['id'], added=image['added'],
                                                  file_loc=image['file_loc'], used=image['used'],
                                                  invoke=image['invoke']))

    def populate_song_list(self):
        self.song_list = []
        with database_connection(self.engine) as db_c:
            for song in db_c.execute(sqlalchemy.sql.select([songs])):
                self.song_list.append(SongsData(id_=song['id'], invoke=song['invoke'],
                                                file_loc=song['file_loc'], artist=song['artist'],
                                                name=song['name'], added=song['added'],
                                                used=song['used'], skipped=song['skipped'],
                                                shuffled=song['shuffled'], volume=song['volume']))


def main():
    print("Loading...")
    client = Ionify(jaz_debug=True)
    try:
        client.run(TOKEN)
    except TimeoutError:
        print(ERROR_NO_CONN)

if __name__ == '__main__':
    check_database()
    main()
