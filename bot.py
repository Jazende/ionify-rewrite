from statics import *

from cfg import TOKEN
from cog_images import IonImages
from discord.ext.commands import Bot
from aiohttp.client_exceptions import ClientConnectorError

import discord


class Ionify(Bot):
    async def on_ready(self):
        print("Logged in as {0}!".format(self.user))
        await self.change_presence(status = discord.Status.offline)

def main():
    print("Loading...")
    client = Ionify("!", self_bot = False)
    client.add_cog(IonImages(client))
    try:
        client.run(TOKEN)
    except TimeoutError:
        print(ERROR_NO_CONN)
    except ClientConnectorError:
        print(ERROR_NO_CONN)

if __name__ == '__main__':
    main()
