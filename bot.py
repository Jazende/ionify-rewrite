from models import *
from statics import *
from dataclasses import *

from cfg import TOKEN, db_loc
from utils import load_opus_library, database_connection, CHANNEL_TEST

import os
import asyncio
import discord
import create_db
import sqlalchemy


def check_database():
    if not os.path.isfile(db_loc):
        engine = sqlalchemy.create_engine(db_loc)
        create_db.create_all_tables(engine)


class Ionify(discord.Client):
    def __init__(self):
        super().__init__()
        self.engine = sqlalchemy.create_engine(db_loc)
        self.sql_select_all_songs = sqlalchemy.sql.select([songs])
        self.image_list = []
        self.populate_image_list()

    async def on_ready(self):
        print("Logged in as {0}!".format(self.user))
        if self.JAZ_DEBUG:
            await self.change_presence(status = discord.Status.offline)

    async def on_message(self, message):
        if message.content.startswith("!"):
            
            # logging all commands
            print(PRINT_MESSAGE.format(message))
            log_ins = log.insert().values(author = str(message.author),
                                          message = str(message.content),
                                          timestamp = datetime.utcnow())
            with database_connection(self.engine) as db_c:
                db_c.execute(log_ins)
            
            if message.content.startswith("!song random"):
                await self.song_random(message)
            elif message.content.startswith("!song playing"):
                await self.song_playing(message)
            elif message.content.startswith("!song shuffle start"):
                await self.song_shuffle_start(message)
            elif message.content.startswith("!song shuffle stop"):
                await self.song_shuffle_stop(message)
            elif message.content.startswith("!song skip"):
                await self.song_skip(message)
            elif message.content.startswith("!song stop"):
                await self.song_stop(message)
            elif message.content.startswith("!song pause"):
                await self.song_pause(message)
            elif message.content.startswith("!song resume"):
                await self.song_resume(message)
            elif message.content.startswith("!song volume"):
                await self.song_volume(message)
            elif message.content.startswith("!song add"):       # <name> <link>
                await self.song_add(message)
            elif message.content.startswith("!song queue"):
                await self.song_queue(message)
            elif message.content.startswith("!song list update"):
                await self.song_list_update(message)
            elif message.content.startswith("!song list"):
                await self.song_list(message)
            elif message.content.startswith("!image add"):      # <name> <link>
                await self.image_add(message)
            elif message.content.startswith("!INSTANT CIRCUS"):
                await self.INSTANT_CIRCUS(message)
            elif message.content.startswith("!INSTANT STOP"):
                await self.INSTANT_STOP(message)
            elif message.content.startswith("!monika text"):    # <text>
                await self.monika_text(message)
            elif message.content.startswith("!monika online"):
                await self.monika_online(message)
            elif message.content.startswith("!monika offline"):
                await self.monika_offline(message)
            elif message.content.startswith("!monika playing"):
                await self.monika_playing(message)
            elif message.content.startswith("!monika commands"):
                await self.monika_commands(message)
            elif message.content.startswith("!song "):
                await self.play_song(message)
        for image_obj in self.image_list:
            if image_obj.match.match(str(message.content).lower()):
                if self.JAZ_DEBUG:
                    chl = message.channel.guild.get_channel(CHANNEL_TEST)
                    await chl.send(file=discord.File(image_obj.file_loc))
                else:
                    await message.channel.send(file=discord.File(image_obj.file_loc))
                image_obj.set_used(self.engine, image_obj.used + 1) 


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
    
    async def song_list(self, message):
        print("!song list")
        pass
    
    async def song_list_update(self, message):
        print("!song list update")
        pass
    
    async def image_add(self, message):
        print("!image add <name> <link>")
        pass
    
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
        print("!play_song")
        pass

    def populate_image_list(self):
        self.image_list = []
        with database_connection(self.engine) as db_c:
            for image in db_c.execute(sqlalchemy.sql.select([images])):
                self.image_list.append(ImagesData(id_=image['id'], added=image['added'],
                                                  file_loc=image['file_loc'], used=image['used'],
                                                  invoke=image['invoke']))


def main():
    print("Loading...")
    client = Ionify()
    client.JAZ_DEBUG = True
    try:
        client.run(TOKEN)
    except TimeoutError:
        print(ERROR_NO_CONN)

if __name__ == '__main__':
    check_database()
    main()
