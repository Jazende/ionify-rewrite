from cfg import TOKEN
from aiohttp.client_exceptions import ClientConnectorError
from statics import error_messages
import discord


class Ionify(discord.Client):
    async def on_ready(self):
        print("Logged in as {0}!".format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))


def main():
    client = Ionify()
    try:
        client.run(TOKEN)
    except TimeoutError:
        print("No connection to Discord. Check network. " + \
              "If on windows, try bypass.")
    except ClientConnectorError:
        print("No connection to Discord. Check network. " + \
              "If on windows, try bypass.")
        

if __name__ == '__main__':
    main()
