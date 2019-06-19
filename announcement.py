import asyncio
import discord
import pytz

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pytz import timezone
from discord.ext import commands
from bot_config import DISCORD_TOKEN, DISCORD_TOKEN_DEV, MY_DISCORD_NAME, MY_DISCORD_ID, db
import bot_helper


'''
This program will make announcement to every user in the DB upon on start
'''

error_color = 0xFF5C5C
success_color = 0x00BF00
warning_color = 0xF4F442
feedback_color = 0x6FA8DC # blue
notify_color = 0xFF9900 # orange



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

        for count, user in enumerate(db.users.find()):

            if count > 3:
                user_id = user["DISCORD_ID"]
                print(count, user_id)
                await self.notify_user(user_id)
        print("DONE")
        

    async def on_message(self, message):


        # don't respond to ourselves
        if message.author == self.user:
            return
        # don't react to other bots
        if message.author.bot:
            return

    
    async def notify_user(self, user_id):
        user = client.get_user(user_id)

        if (user is None):

            # if user id is invalid, may be due to delete discord account
            await bot_helper.remove_user(user_id)
            print("Deleted invalid user :" + str(user_id))
            delete_user_report = discord.Embed(title="Delete Invalid User", description="Deleted invalid user :" + str(user_id), color=feedback_color) 
            await client.get_user(MY_DISCORD_ID).send(embed=delete_user_report)
            return
            
        announcement = discord.Embed(title="Announcement", description="muda!", color=success_color)
        announcement.add_field(name="NovaTracker now accept both item name or item ID when using !track and !untrack command", value="Example usage become **!track ed magic** or **!track 6755**", inline=False)
        announcement.add_field(name="Tracking limit has increased to **10**", value="yes", inline=False)
        announcement.add_field(name="Introducing the new !lowest command", value="Display the lowest selling price on market for your tracking items", inline=False)

        try:
            #await user.send(embed=announcement)
        except Exception as e:
            print("Cannot dm to user " + user_id)





client = MyClient()
client.run(DISCORD_TOKEN)

#DISCORD_TOKEN_DEV, DISCORD_TOKEN


