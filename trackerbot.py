import asyncio
import discord


from discord.ext import commands
from bot_config import DISCORD_TOKEN
from bot_config import db
from novamarket import check_nova_market


#https://github.com/Rapptz/discord.py
class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.track_nova_market())
        

    
    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('Logged on as', self.user)
        print('------')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'best movie':
            await message.author.send('Die Hard')

        if message.content == "!register":
            await message.author.send('Done')

        if message.content.startswith('t'):
            me = client.get_user(294974177184579585)
            await me.send("notifying you")

        

    async def track_nova_market(self):

        await self.wait_until_ready()
        
        while not client.is_closed():
            
            await asyncio.sleep(5)

            print('1 cycle')
            client.get_users()
            '''
            me = client.get_user(294974177184579585)
            await me.send("notifying you")
            '''


    async def get_users(self):

        print('getting user')
        
        #all_users = db.getCollection('users').find({})        

client = MyClient()
client.run(DISCORD_TOKEN)

#py -3.6  trackerbot.py
#python -m pip install discord.py
#https://www.devdungeon.com/content/make-discord-bot-python

#https://www.reddit.com/r/discordapp/comments/8vn61a/is_it_authorized_possible_to_send_a_private/

