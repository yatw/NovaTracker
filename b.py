import asyncio
import discord
import re

from discord.ext import commands
from bot_config import DISCORD_TOKEN
import bot_helper

error_color = 0xFF5C5C
success_color = 0x00BF00
warning_color = 0xF4F442
feedback_color = 0x6FA8DC
notify_color = 0xFF9900



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
        # don't react to other bots
        if message.author.bot:
            return

        if message.content.startswith("!register"):

            user_discord_id = message.author.id
            
            
            if (await bot_helper.already_registrated(user_discord_id)):
                registration_fail = discord.Embed(title="Registration Fail", description="You have already registered", color=error_color) 
                await message.author.send(embed=registration_fail)
                return
            
            await bot_helper.user_register(user_discord_id)
            registration_success = discord.Embed(title="Registration Success", description="you can start tracking items with !track command", color=success_color)
            await message.author.send(embed=registration_success)
            return

        if message.content.startswith("!showtrack"):

            user_discord_id = message.author.id

            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await message.author.send(embed=need_registration)
                return
                

            
            tracking_message = await bot_helper.show_tracking_items(user_discord_id)

            if (tracking_message == ""):
                nothing_on_track = discord.Embed(title="No items tracking", description="You are currently not tracking any item", color=feedback_color) 
                await message.author.send(embed=nothing_on_track)
                return

            tracking_result = discord.Embed(title="You are currently tracking:", description=tracking_message, color=feedback_color)
            await message.author.send(embed=tracking_result)
            return


        if message.content.startswith("!track"):
            # Check if the user is registered
            # Check if the user input is correct
            # Check if the item is alredy tracking
            # TODO Check the user tracking item limit
            # Ask user for confirmation
        
            
            user_discord_id = message.author.id
            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await message.author.send(embed=need_registration)
                return
                
            if (await bot_helper.count_tracking_item(user_discord_id) >= 5):
                max_tracking = discord.Embed(title="Maximum tracking limit", description="You are at your maximum tracking limit (5), try to untrack some items.", color=warning_color)
                await message.author.send(embed=max_tracking)
                return

            
            # correct usage:  !track item_id refine_goal ideal_price(k,m,b all work)
            # example         !track 21018 8 200m

        
            # parse the user input into tokens and return as a dictionary

            result = await bot_helper.parse_track_command(message.content)
       

            if (result["invalid"]): # user input is invalid

                problem_detail = result["problem"]
         
                if ( problem_detail == "Nova Down"):
                    nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                    await message.author.send(embed=nova_down_respond)
                    return


                
                invalid_format_response = "Example Usage is: \n"
                invalid_format_response += "!track item_id refine_goal ideal_price(K,M,B all work)\n!"
                invalid_format_response += "track 21018 8 200m (put 0 if refine not appliable)"
                invalid_tracking_input = discord.Embed(title=problem_detail, description=invalid_format_response, color=warning_color)
                await message.author.send(embed=invalid_tracking_input)
                return
            
            #print(result)
            item_id     = result["item_id"]
            item_name   = result["item_name"]
            refinable   = result["refinable"]
            refine_goal = result["refine_goal"]
            ideal_price = result["ideal_price"]
            
            

                    
            # item not already tracking
            if (await bot_helper.already_tracking(user_discord_id, item_id)):
                    dobule_tracking_response = 'You are already tracking ' + '**' + item_name + '**' + "(" + item_id + ")"
                    double_tracking = discord.Embed(title="Tracking Fail", description=dobule_tracking_response, color=warning_color)
                    await message.author.send(embed=double_tracking)
                    return
    
                
    
            # DO A CONFIRMATION
            confirm_text = "Please type __**CONFIRM**__ to track:"
            confirm_track = discord.Embed(title=confirm_text, color=feedback_color)
            confirm_track.add_field(name="Item", value='**'+item_name+'**', inline=True)

            if (refinable):
                confirm_track.add_field(name="refine >=", value='**'+str(refine_goal)+'**', inline=True)
                
            confirm_track.add_field(name="price <=", value='**'+bot_helper.price_format(ideal_price)+'**', inline=True)
            await message.author.send(embed=confirm_track)

                
            user_confirm_text = await client.wait_for('message', check = lambda message: message.author != self.user and not message.author.bot)
            #print("User confirm text: " + user_confirm_text.content)
        
            if (user_confirm_text.content == "CONFIRM"):
           
                await bot_helper.user_track_item(user_discord_id, item_id, item_name, ideal_price, refinable, refine_goal)

                tracking_success_response = 'Now tracking ' + '**'+ item_name + '**'+ ', you will be notified here when it is on sell <= '  
                tracking_success_response += '**' + bot_helper.price_format(ideal_price) + '**'

                if (refinable):
                    tracking_success_response += " refine >= " + '**' + str(refine_goal) + '**'
                tracking_success = discord.Embed(title="Tracking Success", description=tracking_success_response, color=success_color)
                
                await message.author.send(embed=tracking_success)
                return
            else:

                dismiss_tracking = discord.Embed(title="Dismiss", description='Dismiss Tracking request for ' + item_name, color=warning_color)
                await message.author.send(embed=dismiss_tracking)
                return
            
            return None


        if message.content.startswith('!untrack'):
            # Check if the user is registered
            # Check if the user input is correct
            # TODO Check if the item is alredy tracking
            # Check the user tracking item limit
            # Ask user for confirmation

            user_discord_id = message.author.id
            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await message.author.send(embed=need_registration)
                return
                
            
            # correct usage:  !untrack item_id
            # example         !untrack 21018


            result = await bot_helper.parse_untrack_command(message.content)

            if (result["invalid"]): # untrack input is incorrect

                problem_detail = result["problem"]
         
                if ( problem_detail == "Nova Down"):
                    nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                    await message.author.send(embed=nova_down_respond)
                    return

                
                invalid_format_response = "Example Usage is: \n !untrack item_id\n !untrack 21018"
                invalid_untracking_input = discord.Embed(title=problem_detail, description=invalid_format_response, color=warning_color)
                await message.author.send(embed=invalid_untracking_input)
                return

            item_id = result["item_id"]
            item_name = result["item_name"]

            if not (await bot_helper.already_tracking(user_discord_id, item_id)):

                not_tracking_response = "You have not been tracking " + "**" +item_name + "**"
                not_tracking = discord.Embed(title="Untrack Fail", description=not_tracking_response, color=warning_color)                
                await message.author.send(embed=not_tracking)
                return
        
            await bot_helper.user_untrack_item(user_discord_id, item_id)

            untrack_success_response = "You are no longer tracking " + "**" + item_name + "**"
            untrack_success = discord.Embed(title="Untrack Success", description=untrack_success_response, color=success_color)                
            await message.author.send(embed=untrack_success)
            
            return 


            

        if message.content.startswith('!getname'):

            result = re.findall(r"[A-Za-z0-9]+",message.content)

            input_id = result[1]
            item_name = bot_helper.get_item_name(input_id)
            await message.author.send(item_name)

            return 
        
            
        # For fun stuff all here======================================
    
        if message.content.startswith('!about'):

            await message.author.send("Made with Babyish Love")

    
    async def notify_user(self, user_id, notify_message):
        user = client.get_user(user_id)

        onsell_notification = discord.Embed(title="Item on sell", description=notify_message, color=notify_color)
        await user.send(embed=onsell_notification) 


    async def track_nova_market(self):

        await self.wait_until_ready()
        
        while not client.is_closed():
            
            await asyncio.sleep(900) # 900s = run every 15 minutes
            print("starting cycle")

            try:
                to_notify = bot_helper.handle_user_trackings()
            
                for user_id, message in to_notify:
                    await self.notify_user(user_id,message)
                print("complete cycle")
                    
            except Exception as e:
                print(str(e))           
            

client = MyClient()
client.run(DISCORD_TOKEN)
