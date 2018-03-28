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
import random
import asyncio
import discord
import create_db
import sqlalchemy


def vol_audio_source(song): # Make volume controlled FFmpegPCMAudio from SongsData.file_loc
    loc = os.path.join(BOT_FOLDER_SONGS, song.file_loc)
    print(loc)
    as_ = discord.FFmpegPCMAudio(loc)
    vas = discord.PCMVolumeTransformer(as_)
    vas.volume = max(min(song.volume, 1.5), 0.5)
    return vas


def check_database(): # Checks if DB exists and calls "create_all_tables" if not
    if not os.path.isfile(db_loc):
        engine = sqlalchemy.create_engine(db_loc)
        create_db.create_all_tables(engine)

def check_files():
    if not os.path.isfile(FILE_QUEUE_TRANSFER):
        with open(FILE_QUEUE_TRANSFER, "w") as qt:
            qt.write("")
    if not os.path.isfile(FILE_COMMANDS_TRANSFER):
        with open(FILE_COMMANDS_TRANSFER, "w") as qt:
            qt.write("")

class Ionify(discord.Client):
    def __init__(self, jaz_debug=False):
        super().__init__()
        self.engine = sqlalchemy.create_engine(db_loc)
        self.image_list = []
        self.song_list = []
        self.populate_image_list()
        self.populate_song_list()
        
        self.jaz_debug = jaz_debug
        self.status = BotStatus.stopped
        
        self.vc = None
        self.shuffle = False
        load_opus_library()
        
        
        self.music_commands = asyncio.Queue()
        self.music_queue = asyncio.Queue()
        self.queue_reader = self.loop.create_task(self.loop_read_queue())
        self.command_reader = self.loop.create_task(self.loop_read_commands())
        self.music_commands_loop = self.loop.create_task(self.loop_bot_commands())
        self.music_player = self.loop.create_task(self.loop_music_player())

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
                
            elif message.content.startswith("!toggle shuffle"):
                if self.shuffle:
                    self.shuffle = False
                else:
                    self.shuffle = True
                    
            elif message.content.startswith("!song shuffle start"):
                self.shuffle = True
                await self.music_commands.put(BotCommand.start)
                
            elif message.content.startswith("!song shuffle stop"):
                self.shuffle = False
                
            elif message.content.startswith("!song skip"):          # TODO
                self.vc.stop()
                
            elif message.content.startswith("!song stop"):
                await self.music_commands.put(BotCommand.stop)
                
            elif message.content.startswith("!song pause"):
                await self.music_commands.put(BotCommand.pause)
                
            elif message.content.startswith("!song resume"):
                await self.music_commands.put(BotCommand.resume)
                
            elif message.content.startswith("!volume"):
                # TODO: set default
                if self.vc.is_playing():
                    new_volume = re.findall("!volume ([\d\.]{1,4})$", str(message.content))
                    print(message.content, new_volume)
                    if not new_volume == None:
                        self.vc.source.volume = float(new_volume[0])
                
            elif message.content.startswith("!song add"):       # <name> <link>          # TODO
                await self.song_add(message)

            elif message.content.startswith("!image add"):
                await self.image_add(message)
                
            # elif message.content.startswith("!INSTANT CIRCUS"):
            # elif message.content.startswith("!INSTANT STOP"):
            # elif message.content.startswith("!monika text"): # <text>
            # elif message.content.startswith("!monika online"):
            # elif message.content.startswith("!monika offline"):
            # elif message.content.startswith("!monika playing"):
            # elif message.content.startswith("!monika commands"):
            
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

    async def song_add(self, message):
        print("!song add <name> <link>")
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

    async def play_song(self, message):
        for song in self.song_list:
            if message.content.startswith("!song {}".format(song.invoke)):
                print("matching", song)
                try:
                    await self.music_commands.put(BotCommand.play)
                    await self.music_queue.put(song)
                except BaseException as e:
                    print(e)
                print("done matching")

    async def loop_read_queue(self):
        await self.wait_until_ready()
        while True:
            await asyncio.sleep(10)
            pass
            
    async def loop_read_commands(self):
        await self.wait_until_ready()
        while True:
            with open(FILE_COMMANDS_TRANSFER, "r") as f:
                cmd = f.readline().strip()
            if cmd == "1":
                await self.music_commands.put(BotCommand.stop)
                await asyncio.sleep(1)
            elif cmd == "2":
                await self.music_commands.put(BotCommand.pause)
                await asyncio.sleep(1)
            elif cmd == "3":
                await self.music_commands.put(BotCommand.play)
                await asyncio.sleep(1)
            # elif cmd == "4":
                # await self.music_commands.put(BotCommand.shuffle)
                # await asyncio.sleep(1)
            elif cmd == "5":
                await self.music_commands.put(BotCommand.resume)
            elif cmd == "6":
                await self.music_commands.put(BotCommand.circus)
                await asyncio.sleep(1)
            elif cmd == "7":
                self.vc.stop()
                await asyncio.sleep(1)
            await asyncio.sleep(0.1)
                
    async def loop_bot_commands(self):
        await self.wait_until_ready()
        while True:
            ## TODO lees songs\botcommands.txt
            try:
                data = self.music_commands.get_nowait()
            except asyncio.QueueEmpty as qe:
                await asyncio.sleep(0.5)
            except BaseException as be:
                print(be)
            else:
                self.status = data
                print(self.status)
                self.music_commands.task_done()
            await asyncio.sleep(1)
                
    async def loop_music_player(self):
        await self.wait_until_ready()
        while True:
            if self.status == BotCommand.pause:
                if self.vc.is_playing():
                    self.vc.pause()
            elif self.status == BotCommand.resume:
                if self.vc.is_paused():
                    self.vc.resume()
                    self.status = BotCommand.play
            elif self.status == BotCommand.stop:
                if self.vc.is_paused() or self.vc.is_playing():
                    self.vc.stop()
            elif self.status == BotCommand.play:
                if not self.vc.is_playing() and not self.vc.is_paused():
                    if self.shuffle:
                        song = random.choice(self.song_list)
                        self.vc.play(vol_audio_source(song))
                    else:
                        try:
                            song = self.music_queue.get_nowait()
                        except asyncio.QueueEmpty as qe:
                            if not self.shuffle:
                                self.status == BotCommand.stop()
                        else:
                            self.music_queue.task_done()
                            print("playing ", song)
                            self.vc.play(vol_audio_source(song))
                elif not self.vc.is_playing() and self.vc.is_paused():
                    self.vc.resume()
                    self.status = BotCommand.play
            await asyncio.sleep(0.5)


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
    check_files()
    main()
