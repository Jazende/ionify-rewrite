from statics import *
from utils import compiled_image_regex
from discord.ext import commands

class IonImages:
    def __init__(self, bot):
        self.bot = bot

    def populate_imagelist(self):
        self.imagelist = []
        with open(BOT_IMG_LIST, 'r') as imglst:
            for imgline in imglst:
                stripped = line.strip()
                img, ext = stripped.split(" ")
                self.imagelist.append((img, compiled_image_regex(img), ext))

    async def on_message(self, message):
        try:
            content = message.content.encode("utf-8")
            print(PRINT_MESSAGE.format(message, content))
        except UnicodeEncodeError as uee:
            pass
        
    @commands.command()
    async def ions(self, context):
        await context.message.channel.send("Go to http://ion.kridder.eu/images")

    @commands.command()
    async def ion(self, context):
        for command in ion_commands:
            if context.message.content.startswith(command['invoke']):
                await command['function'](self, context)
                break

    @commands.command()
    async def private(self, context):
        await self.get_channel(CHANNEL_TEST).send(context.meessage.content[8:])

    async def update_songs(self, context):
        pass
        await context.message.channel.send("updating songs")

    async def go_offline(self, context):
        pass

    async def go_online(self, context):
        pass

    async def show_commands(self, context):
        await self.get_channel(CHANNEL_TEST).send("!ions, !ion update songs, !ion commands")
        #await self.context.message.channel.send("!ions, !ion update songs, !ion commands")

ion_commands = [
    {'invoke': '!ion update songs', 'function': lambda x, y: x.update_songs(y)}
    {'invoke': '!ion offline', 'function': lambda x, y: x.go_offline(y)}
    {'invoke': '!ion online', 'function': lambda x, y: x.go_online(y)}
    {'invoke': '!ion commands', 'function': lambda x: y: x.show_commands(y)}
    ]
