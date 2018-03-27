from models import *
from statics import *
from dataclasses import *

from cfg import TOKEN, db_loc
from utils import database_connection, CHANNEL_TEST
from utils import REGEX_MATCH_IMAGE_ADD, regex_findall
from utils import async_download_picture
from utils import load_opus_library
from datetime import datetime

import os
import re
import discord
import create_db
import sqlalchemy


def vol_audio_source(song): # Make volume controlled FFmpegPCMAudio from SongsData.file_loc
    loc = os.path.join(BOT_FOLDER_SONGS, song.file_loc)
    print(loc)
    as_ = discord.FFmpegPCMAudio(loc)
    vas = discord.PCMVolumeTransformer(as_)
    vas.volume = max(min(song.volume, 1.9), 0.1)
    return vas


def check_database(): # Checks if DB exists and calls "create_all_tables" if not
    if not os.path.isfile(db_loc):
        engine = sqlalchemy.create_engine(db_loc)
        create_db.create_all_tables(engine)


class Ionify(discord.Client):
    def __init__(self, jaz_debug=False):
        super().__init__()
        self.engine = sqlalchemy.create_engine(db_loc)
        self.image_list = []
        self.populate_image_list()
        self.song_list = []
        self.populate_song_list()
        # self.queue_list = []
        # self.populate_queue_list()
        self.jaz_debug = jaz_debug
        self.vc = None
        self.status = BotStatus.stopped
        self.audio_file_playing = None
        load_opus_library()

    async def on_ready(self): # Joins VoiceChannel "CHANNEL_VOICE", goes offline if testing
        print("Logged in as {0}!".format(self.user))
        if self.jaz_debug:
            await self.change_presence(status=discord.Status.offline)
        voice_channel = self.get_channel(CHANNEL_VOICE)
        if isinstance(voice_channel, discord.VoiceChannel):
            self.vc = await self.get_channel(CHANNEL_VOICE).connect()
        else:
            raise ValueError("CHANNEL_VOICE is not a VoiceChannel")

    async def on_message(self, message):
        if message.content.startswith("!"):
            
            if self.jaz_debug: # logging all commands
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
            elif message.content.startswith("!song stop"):
                await self.song_stop(message)
            elif message.content.startswith("!song pause"):
                await self.song_pause(message)
            elif message.content.startswith("!song resume"):
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
            elif message.content.startswith("!song "):
                await self.play_song(message)
            elif message.content.startswith("!test"):              # todo remove when complete
                await self.test_functionality(message)
        else:
            for image_obj in self.image_list: # sends picture if match with ImagesData.invoke
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
        self.play_audio(status=BotCommand.stop)
    
    async def song_pause(self, message):
        self.play_audio(status=BotCommand.pause)
    
    async def song_resume(self, message):
        self.play_audio(status=BotCommand.resume)
    
    async def song_volume(self, message):
        if self.vc.is_playing():
            new_volume = re.findall("!song volume ([\d\.]{1,4})$", str(message.content))
            print(message.content, new_volume)
            if not new_volume == None:
                self.vc.source.volume = float(new_volume[0])
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
    
    async def image_add(self, message): # download image, add image to image_list and DB
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
        for song in self.song_list:
            if message.content.startswith("!song {}".format(song.invoke)):
                self.play_audio(BotCommand.play, song)
        
    def play_audio(self, status = BotCommand.stop, song=None, error=None):
        if not error == None:
            self.vc.stop()
            self.status = BotStatus.stopped
        elif status == BotCommand.stop:
            if self.vc.is_playing():
                self.vc.stop()
        elif status == BotCommand.pause:
            if self.vc.is_playing():
                self.vc.pause()
        elif status == BotCommand.play:
            if song == None:
                raise ValueError("Didn't get a SongsData object for play_audio")
            self.audio_file_playing = {'file': vol_audio_source(song), 'info': song}
            self.vc.play(self.audio_file_playing['file'], after=lambda e: self.play_audio(error = e))
        elif status == BotCommand.shuffle:
            pass
            
            
        elif status == BotCommand.resume:
            if self.vc.is_paused():
                self.vc.resume()
        elif status == BotCommand.circus_start:
            pass
        

    def populate_image_list(self): # empty, and insert all images from DB into image_list
        self.image_list = []
        with database_connection(self.engine) as db_c:
            for image in db_c.execute(sqlalchemy.sql.select([images])):
                self.image_list.append(ImagesData(id_=image['id'], added=image['added'],
                                                  file_loc=image['file_loc'], used=image['used'],
                                                  invoke=image['invoke']))

    def populate_song_list(self): # empty, and insert all songs from DB into songs list
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
