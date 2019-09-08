import asyncio
import discord
import pytz
import sys

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pytz import timezone
from discord.ext import commands
from bot_config import DISCORD_TOKEN, DISCORD_TOKEN_DEV, MY_DISCORD_NAME, MY_DISCORD_ID, db
import bot_helper

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


        for count, user_profile in enumerate(db.users.find()):

            print(count+1, "==============================================")

            await self.list_items(user_profile)
        print("DONE")
        

    async def on_message(self, message):


        # don't respond to ourselves
        if message.author == self.user:
            return
        # don't react to other bots
        if message.author.bot:
            return

    
    async def list_items(self, user_profile):

        user_id = user_profile["DISCORD_ID"]
        
        user = client.get_user(user_id)

        if (user is None):

            # if user id is invalid, may be due to delete discord account
            await bot_helper.remove_user(user_id)
            print("Deleted invalid user :" + str(user_id))
            delete_user_report = discord.Embed(title="Delete Invalid User", description="Deleted invalid user :" + str(user_id), color=feedback_color) 
            await client.get_user(MY_DISCORD_ID).send(embed=delete_user_report)
            return

        print(" " + str(user_id) + " " + user.name.translate(non_bmp_map))
        
                    
        for item_id in user_profile["INTERESTED_ITEMS"]:

            refine_goal = (user_profile["INTERESTED_ITEMS"][item_id]["REFINE_GOAL"])


            message = "is tracking " + bot_helper.get_item_name(item_id) + " (" + item_id + ") "

            if (bot_helper.can_refine(item_id)):
                message += " at +" + str(refine_goal)

            message += ",with price <= " + str(user_profile["INTERESTED_ITEMS"][item_id]["IDEAL_PRICE"])
            print(message)

            item_db = db.items.find_one({"ITEM_ID": item_id})
            
            for refine_level in item_db["REFINE"]:

                if int(refine_level) >= int(refine_goal):

                    if user_profile["DISCORD_ID"] not in item_db["REFINE"][refine_level]:
                        print(str(user["DISCORD_ID"]) + " not in " + item_id + " "+ refine_level)
            




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



