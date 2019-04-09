import asyncio
import discord
import re

from discord.ext import commands
from bot_config import DISCORD_TOKEN, db
from novamarket import check_nova_market, get_item_name


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

        if message.content.startswith("!register"):

            user_discord_id = message.author.id

            if (await self.already_registrated(user_discord_id)):
                await message.author.send('You have already registed!')
                return
            
            await self.user_register(user_discord_id)
            await message.author.send('You are now registed, you can start tracking items with !track command')
            return



        if message.content.startswith("!track"):
            # Check if the user is registered
            # Check if the user input is correct
            # Check if the item is alredy tracking
            # TODO Check the user tracking item limit
            # Ask user for confirmation
        
            
            user_discord_id = message.author.id
            if not(await self.already_registrated(user_discord_id)):
                await message.author.send("Please first registred with !register command")
                return
                
            
            # correct usage:  !track item_id ideal_price refine_goal
            # example         !track 21018 800000000 8

            
            result = await self.vertify_track_command(message.content)

            if (result[0] != 1): # user input is invalid
                invalid_format_response = "Incorrect Format, Example Usage is \n !track item_id ideal_price refine_goal \n !track 21018 800000000 8 " 
                await message.author.send(invalid_format_response)
            

            item_id     = result[1]
            ideal_price = result[2]
            refine_goal = result[3]
            item_name   = result[4]

                    
            # item not already tracking
            if (await self.duplicate_tracking(user_discord_id, item_id)):
                    response = 'You are already tracking ' + item_name
                    await message.author.send(response)
                    return

            # DO A CONFIRMATION
            confirm_text = "Please confirm you want to track " + item_name + " ,refine>= " + str(refine_goal) + " at price <= " + str(ideal_price)
            confirm_text += "\ntype CONFIRM to confirm, anything else to dismiss"
            await message.author.send(confirm_text)

                
            user_confirm_text = await client.wait_for('message')
            print("User confirm text: " + user_confirm_text.content)
        
            if (user_confirm_text.content == "CONFIRM"):
           
                await self.user_track_item(user_discord_id, item_id, ideal_price, refine_goal)
                response = 'Nova Tracker is now tracking ' + item_name + ', you will be notified when this item is on sell under ' +  str(ideal_price) + " at refine greater than" + str(refine_goal)
                await message.author.send(response)
                return
            else:
                await message.author.send('Dismiss Tracking request for ' + item_name)
                return
            
            return None


        if message.content.startswith('!untrack'):
            # Check if the user is registered
            # Check if the user input is correct
            # TODO Check if the item is alredy tracking
            # Check the user tracking item limit
            # Ask user for confirmation

            user_discord_id = message.author.id
            if not(await self.already_registrated(user_discord_id)):
                await message.author.send("Please first registred with !register command")
                return
                
            
            # correct usage:  !untrack item_id
            # example         !untrack 21018

            item_id = await self.vertify_untrack_command(message.content)

            if (item_id == ""):
                await message.author.send("Invalid Format, Example Usage is \n !untrack item_id\n !track 21018")

            item_name = get_item_name(item_id)

            if (item_name == "Unknown"):
                await message.author.send("Item " + item_id + " do not exist, please double check the ITEM ID")
            else:
                await self.user_untrack_item(user_discord_id, item_id)
                await message.author.send("You are no longer tracking " + item_name)
                return 


            
            await message.author.send("Invalid Format, Example Usage is \n !untrack item_id\n !track 21018")


        # For fun stuff all here
    
        if message.content.startswith('about'):
            #me = client.get_user(294974177184579585)
            #await me.send("notifying you")
            await message.author.send("Made with Babyish Love")

    
    async def notify_user(self, user_id):
        me = client.get_user(294974177184579585)
        await me.send("notifying you") 


    async def track_nova_market(self):

        await self.wait_until_ready()
        
        while not client.is_closed():
            
            await asyncio.sleep(5)

            #print('1 cycle')
            

    
    async def already_registrated(self, user_discord_id):
        '''Return True if find user in the database'''


        if (db.users.find({'DISCORD_ID' : user_discord_id}).count() != 0):
            return True

        return False

    async def user_register(self,user_discord_id):

        db.users.insert(
                {
                    'DISCORD_ID' : user_discord_id,
                    'INTERESTED_ITEMS' : []
                }
            )

        return None

    async def vertify_track_command(self, command):
        # correct usage:  !track item_id ideal_price refine_goal
        # example         !track 21018 800000000 8

        try:
            result = re.findall(r"[\w]+",command)

            if (len(result) >= 5):
                raise Exception('Extra parameters')

            item_id = result[1]
            ideal_price = int(result[2])
            if (ideal_price < 0 or ideal_price > 1000000000):
                raise Exception('Invalid Ideal Price')
            result[2] = ideal_price
    
            
            refine_goal = int(result[3])
            if (refine_goal < 0 or refine_goal > 20):
                raise Exception('Invalid Refine Goal')
            result[3] = refine_goal

                

            item_name = get_item_name(item_id)
            if (item_name == "Unknown"):
                raise Exception('Invalid Item ID')
            
            result.append(item_name)
            
            result[0] = 1 # valid
        except:
            result[0] = 0 # not valid


        return result


    async def vertify_untrack_command(self, command):
        # all you have to do is vertify the item_id is valid, but doesn't check if it exist
        # correct usage:  !untrack item_id
        # example         !untrack 21018

        try:
            result = re.findall(r"[\w]+",command)

            if (len(result) >= 3):
                raise Exception('Extra parameters')

            int(result[1]) # check that it is int
            return result[1]

        except:
            return ""


        return ""

    async def duplicate_tracking(self, user_discord_id, item_id):

        user = db.users.find_one({'DISCORD_ID' : user_discord_id})

        user_items = user['INTERESTED_ITEMS']

        for item in user_items:
            if item['ITEM_ID'] == item_id:
                return True

        return False


    async def user_track_item(self,user_discord_id, item_id, ideal_price, refine_goal):

        item_info = {

                'ITEM_ID': item_id,
                'IDEAL_PRICE': ideal_price,
                'REFINE_GOAL': refine_goal

        }

        db.users.update(
            {'DISCORD_ID' : user_discord_id},
            {'$push': {'INTERESTED_ITEMS': item_info}}
        )

       
        return None

    async def user_untrack_item(self, user_discord_id, item_id):

        db.users.update(
            {'DISCORD_ID' : user_discord_id},
            { '$pull': {'INTERESTED_ITEMS': {'ITEM_ID' : item_id}}}
        )

        return None


client = MyClient()
client.run(DISCORD_TOKEN)
