import os
from cfg import BOT_FOLDER

QUEUE_FETCH_DELAY = 5

ERROR_NO_CONN = "No connection to Discord. Check network. If on windows, try bypass."
PRINT_MESSAGE = 'Message from {0.author} in channel {0.channel}: {0.content}'

CHANNEL_TEST = 383215871860015105
# CHANNEL_VOICE = 390557208946933765 # originele voice channel, onderstaande is test
CHANNEL_VOICE = 426405260798459914
CHANNEL_OFFTOPIC = 294536565240233994

BOT_FOLDER_IMAGES = os.path.join(BOT_FOLDER, "images")
BOT_FOLDER_SONGS = os.path.join(BOT_FOLDER, "songs")
