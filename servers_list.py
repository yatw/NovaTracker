import asyncio
import discord
import pytz

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pytz import timezone
from discord.ext import commands
from bot_config import DISCORD_TOKEN, DISCORD_TOKEN_DEV, MY_DISCORD_NAME, MY_DISCORD_ID, db
import bot_helper
import sys



error_color = 0xFF5C5C
success_color = 0x00BF00
warning_color = 0xF4F442
feedback_color = 0x6FA8DC # blue
notify_color = 0xFF9900 # orange

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)


#https://github.com/Rapptz/discord.py
class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    
    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('Logged on as', self.user)
        print('------')
        #await client.user.edit(username="NovaTracker")
        #print("Changed new name to ", client.user.name)

        print("Connected servers")
        servers = list(client.guilds)

        for index in range(len(servers)):
            print("==============================================")
            print(str(index+1) + ' ' + servers[index].name)
            print("==============================================")

            print("members:")

            for count,member in enumerate(servers[index].members):
                print(count, member.name.translate(non_bmp_map))
            
        

    async def on_message(self, message):


        # don't respond to ourselves
        if message.author == self.user:
            return
        # don't react to other bots
        if message.author.bot:
            return



client = MyClient()
client.run(DISCORD_TOKEN)



#DISCORD_TOKEN_DEV, DISCORD_TOKEN



'''
user_interested_items = db.users.find_one({'DISCORD_ID' : asdklfjlask})['INTERESTED_ITEMS']
user_interested_items.pop("6671", None);

db.users.update_one(
    {'DISCORD_ID' : sadfjlkadsjflk},
    { '$set': {'INTERESTED_ITEMS': user_interested_items}}
)
'''



