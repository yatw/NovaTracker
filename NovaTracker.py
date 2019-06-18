import asyncio
import discord
import re
import time
import traceback
import pytz

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pytz import timezone
from discord.ext import commands
from bot_config import DISCORD_TOKEN, DISCORD_TOKEN_DEV, MY_DISCORD_NAME, MY_DISCORD_ID
import bot_helper

error_color = 0xFF5C5C
success_color = 0x00BF00
warning_color = 0xF4F442
feedback_color = 0x6FA8DC # blue
notify_color = 0xFF9900   # orange
crash_title = "Oops it crashes! I am so sorry~~, will fix it ASAP"

tracking_limit = 10

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
        #await client.user.edit(username="NovaTrackerBeta")
        #print("Changed new name to ", client.user.name)

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

            try:
                await bot_helper.user_register(user_discord_id)
                registration_success = discord.Embed(title="Registration Success", description="you can start tracking items with !track command", color=success_color)
                await message.author.send(embed=registration_success)
                
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await message.author.send(embed=crash)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)
                
            return

        if message.content.startswith("!showtrack"):

            user_discord_id = message.author.id

            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await message.author.send(embed=need_registration)
                return
                

            try:
                tracking_message = await bot_helper.show_tracking_items(user_discord_id)
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await message.author.send(embed=crash)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)
                return

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
            # Check the user tracking item limit
            # Ask user for confirmation

        
            # Check if the user is registered
            user_discord_id = message.author.id
            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await message.author.send(embed=need_registration)
                return

            # Check the user tracking item limit
            if (await bot_helper.count_tracking_item(user_discord_id) >= tracking_limit) and user_discord_id != MY_DISCORD_ID:
                max_tracking = discord.Embed(title="Maximum tracking limit", description="You are at your maximum tracking limit ("+tracking_limit+"), try to untrack some items.", color=warning_color)
                await message.author.send(embed=max_tracking)
                return

            
            # correct usage:  !track item_id/name
            # example         !track 21018

        
            # parse the user input

            search_term = await bot_helper.parse_track_command(message.content)

            #input_type 1 is item_id
            #input_type 2 is search string

            if (search_term is None):
         
                invalid_format_response = "Example Usage is: \n"
                invalid_format_response += "!track item_id/item name \n"
                invalid_format_response += "!track ed magic"
                invalid_tracking_input = discord.Embed(title=search_term, description=invalid_format_response, color=warning_color)
                await message.author.send(embed=invalid_tracking_input)
                return


            item_id = None
            item_name = None

            # user type in item_id
            if search_term.isdigit():

                item_id = search_term
                item_name = bot_helper.get_item_name(item_id)

                if (item_name == "Unknown"):
                    no_result_respond = discord.Embed(title="No item found", description="There is no item with id " + search_term, color=warning_color)
                    await message.author.send(embed=no_result_respond)
                    return

            # user type in item name
            else:

                try:
                    search_matches = bot_helper.search_item(search_term)
                    
                except Exception as e:
                    
                    nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                    await message.author.send(embed=nova_down_respond)
                    return

                                
                if search_matches is None:
                    no_result_respond = discord.Embed(title="No item found", description="There is no search result for " + search_term + ", try using item id", color=warning_color)
                    await message.author.send(embed=no_result_respond)
                    return


                ### PROMPT for selection/ item_id /item_name

                index = 0
                
                if len(search_matches) > 1:


                    select_item = discord.Embed(title="Please __**Enter the index**__ to select the item, type anything else to dismiss", description=str(len(search_matches)) + " results", color=feedback_color)

                    count = 0
                    for match in search_matches:
                        count += 1
                        select_item.add_field(name="Index: " + str(count), value="**" + match[0] + "** (" + match[1] + ")", inline=False)
                        
                    await message.author.send(embed=select_item)
                    user_input_index = await client.wait_for('message', check = lambda message: message.author != self.user and not message.author.bot)

                    try:
                        user_input_index = int(user_input_index.content)
                        if (user_input_index < 1 or user_input_index > count):
                            raise Exception("Invalid Index")
                        index = user_input_index -1
                        
                        
                    except Exception as e:
                        dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                        await message.author.send(embed=dismiss_select)
                        return
                    
                item_id = search_matches[index][1]
                item_name = search_matches[index][0]       

                    
            # item already tracking
            if (await bot_helper.already_tracking(user_discord_id, item_id)):
                    dobule_tracking_response = 'You are already tracking ' + '**' + item_name + '**' + "(" + item_id + ")"
                    double_tracking = discord.Embed(title="Tracking Fail", description=dobule_tracking_response, color=warning_color)
                    await message.author.send(embed=double_tracking)
                    return

            try:
                refinable = bot_helper.can_refine(item_id) # can_refine can fail if Nova is down
                
            except Exception as e:
                nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                await message.author.send(embed=nova_down_respond)
                return
                
            refine_goal = 0
            ideal_price = 0    

            ### PROMPT for ideal_price

            
            enter_ideal_price = discord.Embed(title="You selected " + "**"+item_name+"**" + " (" + item_id + ")", description="Enter your ideal price (K,M,B all work)", color=feedback_color)
            await message.author.send(embed=enter_ideal_price)
            
            user_input_ideal_price = await client.wait_for('message', check = lambda message: message.author != self.user and not message.author.bot)

            try:
                user_input_ideal_price = int(bot_helper.to_price(user_input_ideal_price.content))

                if (user_input_ideal_price < 1 or user_input_ideal_price > 1000000000):
                    raise Exception('Valid price range is 1 to 1,000,000,000')
                
                ideal_price = user_input_ideal_price

            except Exception as e:
                dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                await message.author.send(embed=dismiss_select)
                return
                        

            ### PROMPT for refine_goal
            if (refinable):

                
                enter_refine_level = discord.Embed(title="Enter a refine goal", description="0-20, type anything else to dismiss", color=feedback_color)
                await message.author.send(embed=enter_refine_level)
                
                user_input_refine_goal = await client.wait_for('message', check = lambda message: message.author != self.user and not message.author.bot)

                try:
                    user_input_refine_goal = int(user_input_refine_goal.content)
                    if (user_input_refine_goal < 0 or user_input_refine_goal > 20):
                        raise Exception('Valid refine is 0 to 20')
                    refine_goal = user_input_refine_goal

                except Exception as e:
                    dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                    await message.author.send(embed=dismiss_select)
                    return
    
                
    
            # DO A CONFIRMATION
            confirm_text = "Please type __**CONFIRM**__ to track:"
            confirm_track = discord.Embed(title=confirm_text, color=feedback_color)
            confirm_track.add_field(name="Item", value='**'+item_name+'**', inline=True)

            if (refinable):
                confirm_track.add_field(name="refine >=", value='**'+str(refine_goal)+'**', inline=True)
                
            confirm_track.add_field(name="price <=", value='**'+bot_helper.price_format(ideal_price)+'**', inline=True)

            # debug purpose line
            confirm_track.add_field(name="-----------  System think it is Refinable = " + str(refinable) + "-----------", value="For debug purpose, please dismiss and !report if you believe the system is wrong", inline=False)
                
            await message.author.send(embed=confirm_track)

                
            user_confirm_text = await client.wait_for('message', check = lambda message: message.author != self.user and not message.author.bot)
            #print("User confirm text: " + user_confirm_text.content)
        
            if (user_confirm_text.content == "CONFIRM"):


                try:
               
                    await bot_helper.user_track_item(user_discord_id, item_id, item_name, ideal_price, refinable, refine_goal)

                    tracking_success_response = 'Now tracking ' + '**'+ item_name + '**'+ " ("+ item_id + ")"+ ', you will be notified here when it is on sell <= '  
                    tracking_success_response += '**' + bot_helper.price_format(ideal_price) + '**'

                    if (refinable):
                        tracking_success_response += " refine >= " + '**' + str(refine_goal) + '**'
                    tracking_success = discord.Embed(title="Tracking Success", description=tracking_success_response, color=success_color)
                    
                    await message.author.send(embed=tracking_success)

                    
                except Exception as e:
                    crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                    await message.author.send(embed=crash)
                    await client.get_user(MY_DISCORD_ID).send(embed=crash)
                    
                return
            else:

                dismiss_tracking = discord.Embed(title="Dismiss", description='Dismiss Tracking request for ' + item_name, color=warning_color)
                await message.author.send(embed=dismiss_tracking)
                return
            
            return None


        if message.content.startswith('!untrack'):
            # Check if the user is registered
            # Check if the user input is correct
            # Check if the item is alredy tracking


            user_discord_id = message.author.id
            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await message.author.send(embed=need_registration)
                return
                
            
            # correct usage:  !untrack item_id/item_name
            # example         !untrack 21018


            search_term = await bot_helper.parse_track_command(message.content)

            if (search_term is None):
         
                invalid_format_response = "Example Usage is: \n !untrack item_id\n !untrack 21018"
                invalid_tracking_input = discord.Embed(title=search_term, description=invalid_format_response, color=warning_color)
                await message.author.send(embed=invalid_tracking_input)
                return

            item_id = None
            item_name = None

            # user type in item_id
            if search_term.isdigit():

                item_id = search_term
                item_name = bot_helper.get_item_name(item_id)

                if (item_name == "Unknown"):
                    no_result_respond = discord.Embed(title="No item found", description="There is no search result for " + search_term, color=warning_color)
                    await message.author.send(embed=no_result_respond)
                    return

            # user type in item_name
            else:

                try:
                    search_matches = bot_helper.search_item(search_term)
                    
                except Exception as e:
                    
                    nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                    await message.author.send(embed=nova_down_respond)
                    return

                                
                if search_matches is None:
                    no_result_respond = discord.Embed(title="No item found", description="There is no search result for " + search_term + ", try using item id", color=warning_color)
                    await message.author.send(embed=no_result_respond)
                    return


                ### PROMPT for selection/ item_id /item_name

                index = 0
                
                if len(search_matches) > 1:


                    select_item = discord.Embed(title="Please __**Enter the index**__ to select the item, type anything else to dismiss", description=str(len(search_matches)) + " results", color=feedback_color)

                    count = 0
                    for match in search_matches:
                        count += 1
                        select_item.add_field(name="Index: " + str(count), value="**" + match[0] + "** (" + match[1] + ")", inline=False)
                        
                    await message.author.send(embed=select_item)
                    user_input_index = await client.wait_for('message', check = lambda message: message.author != self.user and not message.author.bot)

                    try:
                        user_input_index = int(user_input_index.content)
                        if (user_input_index < 1 or user_input_index > count):
                            raise Exception("Invalid Index")
                        index = user_input_index -1
                        
                        
                    except Exception as e:
                        dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                        await message.author.send(embed=dismiss_select)
                        return
                    
                item_id = search_matches[index][1]
                item_name = search_matches[index][0]


            if not (await bot_helper.already_tracking(user_discord_id, item_id)):

                not_tracking_response = "You have not been tracking " + "**" +item_name + "**" + " (" + item_id + ")"
                not_tracking = discord.Embed(title="Untrack Fail", description=not_tracking_response, color=warning_color)                
                await message.author.send(embed=not_tracking)
                return

            try:
                await bot_helper.user_untrack_item(user_discord_id, item_id)

                untrack_success_response = "You are no longer tracking " + "**" + item_name + "**" + " (" + item_id + ")"
                untrack_success = discord.Embed(title="Untrack Success", description=untrack_success_response, color=success_color)                
                await message.author.send(embed=untrack_success)
                
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await message.author.send(embed=crash)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)

            return 



        if message.content.startswith('!lowest'):

            user_discord_id = message.author.id

            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await message.author.send(embed=need_registration)
                return
                
            try:
                lowest_report = await bot_helper.get_lowest(user_discord_id)
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await message.author.send(embed=crash)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)
                return

            if (lowest_report == []):
                nothing_on_track = discord.Embed(title="No items tracking", description="You are currently not tracking any item", color=feedback_color) 
                await message.author.send(embed=nothing_on_track)
                return

            for result in lowest_report:
                await self.notify_user(user_discord_id,result)

            return





        if message.content.startswith('!report'):
            await message.author.send("Thank you for your report, this feature is coming soon, use !contact for now")
            


        if message.content.startswith('!help'):

            embed=discord.Embed(title="NovaTracker Commands", description="Please support this bot by telling your friends!", color=feedback_color)
            embed.add_field(name="!start", value="Give a brief description of this bot for first time user", inline=False)
            embed.add_field(name="!about", value="Display user number and bot status", inline=False)
            embed.add_field(name="!register", value="Initialize user in the database, this registration is bond to the user's discord id", inline=False)
            embed.add_field(name="!track", value="**Where the fun begin!**", inline=False)
            embed.add_field(name="!untrack", value="Stop tracking the item", inline=False)
            embed.add_field(name="!showtrack", value="List all the items user is currently tracking", inline=False)
            embed.add_field(name="!lowest", value="Display the lowest price of the tracking items currently on market", inline=False)
            embed.add_field(name="!report", value="Allow user to report bug", inline=False)
            embed.add_field(name="!contact", value="Show my discord name for contact", inline=False)
            embed.add_field(name="!quote", value="Show my favourite quote at the moment", inline=False)
            embed.add_field(name="!help", value="List all the commands for this bot", inline=False)
            
            await message.author.send(embed=embed)


        if message.content.startswith('!start'):

            bot_description = "Nova Tracker is a discord bot to help user track items on sell in the market\n"
            bot_description += "It personalizes your tracking preference and notifies you directly on discord\n"
            bot_description += "This bot handles all messages directly so just pm it like a discord user\n"
            bot_description += "Do notice that if Nova website is down this bot will also be down\n"
            bot_description += "**Start using it by typing !help**\n"
     
            start_message = discord.Embed(title="Start using NovaTracker", description=bot_description, color=feedback_color)                
            await message.channel.send(embed=start_message)
            
        # For fun stuff all here======================================
    
        if message.content.startswith('!about'):

            user_numbers = bot_helper.get_user_number()

            about_text = "Currently on Version 1.0 "
            about_text += "with " + "**"+str(user_numbers)+ "**" + " users\n"
            about_text += "Please support this bot by telling your friends!"
            about_message = discord.Embed(title="Made with Babyish Love", description=about_text, color=feedback_color)                
            await message.author.send(embed=about_message)

        if message.content.startswith('!quote'):
            
            quote = discord.Embed(title="if you experience hell first, then everything is heaven to you - by Babyish Love", color=feedback_color)                
            await message.author.send(embed=quote)


        if message.content.startswith('!contact'):
            
            contact_info = discord.Embed(title="Contact Info", description=MY_DISCORD_NAME, color=feedback_color)                
            await message.author.send(embed=contact_info)

    
    async def notify_user(self, user_id, notify_message):
        user = client.get_user(user_id)

        if (user is None):

            # if user id is invalid, may be due to delete discord account
            await bot_helper.remove_user(user_id)
            print("Deleted invalid user :" + str(user_id))
            delete_user_report = discord.Embed(title="Delete Invalid User", description="Deleted invalid user :" + str(user_id), color=feedback_color) 
            await client.get_user(MY_DISCORD_ID).send(embed=delete_user_report)
            return

        onsell_notification = discord.Embed(title="Item on sell", description=notify_message, color=notify_color)
        await user.send(embed=onsell_notification) 


    async def track_nova_market(self):

        await self.wait_until_ready()
        
        while not client.is_closed():
            
            await asyncio.sleep(900) # 900s = run every 15 minutes
            
            now = datetime.now(tz=pytz.utc)
            now = now.astimezone(timezone('US/Pacific'))
            
            print("Starting cycle at " + now.strftime("%Y-%m-%d %H:%M %p"))

            
            try:
                '''
                loop = asyncio.get_event_loop()
                to_notify = await loop.run_in_executor(ThreadPoolExecutor(), bot_helper.handle_user_trackings)
            
                for user_id, message in to_notify:
                    await self.notify_user(user_id,message)
                '''
                print("Complete cycle at " + now.strftime("%Y-%m-%d %H:%M %p"))
                                
            except Exception as e:
                print("Problem in cycle at " + now.strftime("%Y-%m-%d %H:%M %p"))
                crash_title_for_me = "Problem in cycle at " + now.strftime("%Y-%m-%d %H:%M %p")
                crash = discord.Embed(title=crash_title_for_me, description=traceback.format_exc(), color=error_color) 
                await client.get_user(MY_DISCORD_ID).send(embed=crash)

        return


client = MyClient()
client.run(DISCORD_TOKEN_DEV)

#DISCORD_TOKEN_DEV, DISCORD_TOKEN


