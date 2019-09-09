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
from bot_config import DOC_LINK,DISCORD_TOKEN, DISCORD_TOKEN_DEV, MY_DISCORD_NAME, MY_DISCORD_ID
import bot_helper
import bot_quotes

error_color = 0xFF5C5C    # red
success_color = 0x00BF00  # green
warning_color = 0xF4F442  # yellow
feedback_color = 0x6FA8DC # blue
notify_color = 0xFF9900   # orange
crash_title = "Oops it crashes! I am so sorry~~, will fix it ASAP"

tracking_limit = 10
version = 1.4

#https://github.com/Rapptz/discord.py
class MyClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg_task = self.loop.create_task(self.track_nova_market())
        self.q = bot_quotes.Quotes()
        self.show_run = True

    
    async def on_ready(self):
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('Logged on as', self.user)
        print('------')
        #await client.user.edit(username="NovaTracker")
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
                await self.message_user(user_discord_id, registration_fail, message.channel)
                return

            try:
                await bot_helper.user_register(user_discord_id)
                registration_success = discord.Embed(title="Registration Success", description="you can start tracking items with !track [name/id] command", color=success_color)
                await self.message_user(user_discord_id, registration_success, message.channel)

                thankyou_note = discord.Embed(title="Thank You", description="If you can give it that much of a chance, I can already thank you", color=success_color)
                await self.message_user(user_discord_id, thankyou_note, message.channel)

                user_numbers = bot_helper.get_user_number()
                increase_user_report = discord.Embed(title="New User Register", description= str(user_discord_id) + " just registered, total user number is: " +  "**"+str(user_numbers)+ "**", color=feedback_color) 
                await client.get_user(MY_DISCORD_ID).send(embed=increase_user_report)
                
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await self.message_user(user_discord_id, crash, message.channel)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)
                
            return None

        if message.content.startswith("!showtrack"):

            user_discord_id = message.author.id

            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await self.message_user(user_discord_id, need_registration, message.channel)
                return
                

            try:
                tracking_message = await bot_helper.show_tracking_items(user_discord_id)
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await self.message_user(user_discord_id, crash, message.channel)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)
                return

            if (tracking_message == ""):
                nothing_on_track = discord.Embed(title="No items tracking", description="You are currently not tracking any item", color=feedback_color) 
                await self.message_user(user_discord_id, nothing_on_track, message.channel)
                return

            tracking_result = discord.Embed(title="You are currently tracking:", description=tracking_message, color=feedback_color)
            await self.message_user(user_discord_id, tracking_result, message.channel)
            return None


        if message.content.startswith("!track"):
            # Check if the user is registered
            # Check if the user input is correct
            # Check if the item is alredy tracking
            # Check the user tracking item limit
            # Ask user for confirmation

        
            # Check if the user is registered
            user = message.author
            user_discord_id = message.author.id
            
            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await self.message_user(user_discord_id, need_registration, message.channel)
                return

            # Check the user tracking item limit
            if (await bot_helper.count_tracking_item(user_discord_id) >= tracking_limit) and user_discord_id != MY_DISCORD_ID:
                max_tracking = discord.Embed(title="Maximum tracking limit", description="You are at your maximum tracking limit ("+ str(tracking_limit)+ "), try to untrack some items.", color=warning_color)
                await self.message_user(user_discord_id, max_tracking, message.channel)
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
                invalid_format_response += "!track !track 21018 or !track lindy hop"
                invalid_tracking_input = discord.Embed(title=search_term, description=invalid_format_response, color=warning_color)
                await self.message_user(user_discord_id, invalid_tracking_input, message.channel)
                return


            item_id = None
            item_name = None

            # user type in item_id
            if search_term.isdigit():

                item_id = search_term
                item_name = bot_helper.get_item_name(item_id)

                if (item_name == "Unknown"):
                    no_result_respond = discord.Embed(title="No item found", description="There is no item with ID " + search_term, color=warning_color)
                    await self.message_user(user_discord_id, no_result_respond, message.channel)
                    return

            # user type in item name
            else:

                try:
                    search_matches = bot_helper.search_item(search_term)
                    
                except Exception as e:
                    
                    nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                    await self.message_user(user_discord_id, nova_down_respond, message.channel)
                    return

                                
                if search_matches is None:
                    no_result_respond = discord.Embed(title="No item found", description="There is no search result for " + search_term + ", try using item id", color=warning_color)
                    await self.message_user(user_discord_id, no_result_respond, message.channel)
                    return


                ### PROMPT for selection/ item_id /item_name

                index = 0
                
                if len(search_matches) > 1:


                    select_item = discord.Embed(title="Please __**Enter the index**__ to select the item, type anything else to dismiss", description=str(len(search_matches)) + " results", color=feedback_color)

                    count = 0
                    for match in search_matches:
                        count += 1
                        select_item.add_field(name="Index: " + str(count), value="**" + match[0] + "** (" + match[1] + ")", inline=False)
                        
                    await self.message_user(user_discord_id, select_item, message.channel)

                    # Get user input
                    try:
                        user_input_index = await client.wait_for('message', check = lambda message: message.author == user , timeout=120.0)

                    except asyncio.TimeoutError:
                        dismiss_select = discord.Embed(title="Dismiss", description="Automatically dismiss after 2 minutes", color=warning_color)
                        await self.message_user(user_discord_id, dismiss_select, message.channel)
                        return

                    
                    try:

                        user_input_index = int(user_input_index.content)
                        if (user_input_index < 1 or user_input_index > count):
                            raise Exception("Invalid Index")
                        index = user_input_index -1
                        
                        
                    except Exception as e:
                        dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                        await self.message_user(user_discord_id, dismiss_select, message.channel)
                        return
                    
                item_id = search_matches[index][1]
                item_name = search_matches[index][0]       

                    
            # item already tracking
            if (await bot_helper.already_tracking(user_discord_id, item_id)):
                    dobule_tracking_response = 'You are already tracking ' + '**' + item_name + '**' + "(" + item_id + ")"
                    double_tracking = discord.Embed(title="Tracking Fail", description=dobule_tracking_response, color=warning_color)
                    await self.message_user(user_discord_id, double_tracking, message.channel)
                    return
            else:
                item_selected = discord.Embed(title="You selected " + "**"+item_name+"**" + " (" + item_id + ")", description=" ", color=feedback_color)
                await self.message_user(user_discord_id, item_selected, message.channel)


            try:
                refinable = bot_helper.can_refine(item_id) # can_refine can fail if Nova is down
                
            except Exception as e:
                nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                await self.message_user(user_discord_id, nova_down_respond, message.channel)
                return
                
            refine_goal = 0
            ideal_price = 0



            ### PROMPT for refine_goal
            if (refinable):
                
                enter_refine_level = discord.Embed(title="Enter a refine goal, get notify when the refine is at least >= ?", description="0-20, type anything else to dismiss", color=feedback_color)
                await self.message_user(user_discord_id, enter_refine_level, message.channel)

                # Get user input
                try:
                    user_input_refine_goal = await client.wait_for('message', check = lambda message: message.author == user, timeout=120.0)

                except asyncio.TimeoutError:
                    dismiss_select = discord.Embed(title="Dismiss", description="Automatically dismiss after 2 minutes", color=warning_color)
                    await self.message_user(user_discord_id, dismiss_select, message.channel)
                    return
                    
                try:

                    user_input_refine_goal = int(user_input_refine_goal.content)
                    if (user_input_refine_goal < 0 or user_input_refine_goal > 20):
                        raise Exception('Valid refine is 0 to 20')
                    refine_goal = user_input_refine_goal

                except Exception as e:
                    dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                    await self.message_user(user_discord_id, dismiss_select, message.channel)
                    return

            ### PROMPT for ideal_price
            
            enter_ideal_price = discord.Embed(title="Enter your ideal price, get notify when the price is <= ?", description="(accept k = 000, m = 000,000, and b = 000,000,000), etc 50m", color=feedback_color)
            await self.message_user(user_discord_id, enter_ideal_price, message.channel)

            # Get user input
            try:
                user_input_ideal_price = await client.wait_for('message', check = lambda message: message.author == user, timeout=120.0)

            except asyncio.TimeoutError:
                dismiss_select = discord.Embed(title="Dismiss", description="Automatically dismiss after 2 minutes", color=warning_color)
                await self.message_user(user_discord_id, dismiss_select, message.channel)
                return

            
            try:

                user_input_ideal_price = int(bot_helper.to_price(user_input_ideal_price.content))

                if (user_input_ideal_price < 1 or user_input_ideal_price > 1000000000):
                    raise Exception('Valid price range is 1 to 1,000,000,000')
                
                ideal_price = user_input_ideal_price

            except Exception as e:
                dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                await self.message_user(user_discord_id, dismiss_select, message.channel)
                return
    
                
    
            # DO A CONFIRMATION
            confirm_text = "Please type __**CONFIRM**__ to track:"
            confirm_track = discord.Embed(title=confirm_text, color=feedback_color)
            confirm_track.add_field(name="Item", value='**'+item_name+ " (" + item_id + ")" + '**' , inline=True)

            if (refinable):
                confirm_track.add_field(name="refine >=", value='**'+str(refine_goal)+'**', inline=True)
                
            confirm_track.add_field(name="price <=", value='**'+bot_helper.price_format(ideal_price)+'**', inline=True)

            # debug purpose line
            confirm_track.add_field(name="-----------  System think it is Refinable = " + str(refinable) + "-----------", value="For debug purpose, please dismiss and !report if you believe the system is wrong", inline=False)
                
            await self.message_user(user_discord_id, confirm_track, message.channel)

            # Get user input
            try:
                user_confirm_text = await client.wait_for('message', check = lambda message: message.author == user, timeout=120.0)
                #print("User confirm text: " + user_confirm_text.content)
                
            except asyncio.TimeoutError:
                dismiss_select = discord.Embed(title="Dismiss", description="Automatically dismiss after 2 minutes", color=warning_color)
                await self.message_user(user_discord_id, dismiss_select, message.channel)
                return
            
            if (user_confirm_text.content == "CONFIRM"):


                try:
               
                    await bot_helper.user_track_item(user_discord_id, item_id, item_name, ideal_price, refinable, refine_goal)

                    tracking_success_response = 'Now tracking ' + '**'+ item_name + '**'+ " ("+ item_id + ")"+ ', you will be notified here when it is on sell <= '  
                    tracking_success_response += '**' + bot_helper.price_format(ideal_price) + '**'

                    if (refinable):
                        tracking_success_response += " refine >= " + '**' + str(refine_goal) + '**'
                    tracking_success = discord.Embed(title="Tracking Success", description=tracking_success_response, color=success_color)
                    
                    await self.message_user(user_discord_id, tracking_success, message.channel)

                    
                except Exception as e:
                    crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                    await self.message_user(user_discord_id, crash, message.channel)
                    await client.get_user(MY_DISCORD_ID).send(embed=crash)
                    
                return
            else:

                dismiss_tracking = discord.Embed(title='Dismiss tracking request for ' + item_name, description="Make sure you use uppercase __**CONFIRM**__", color=warning_color)
                await self.message_user(user_discord_id, dismiss_tracking, message.channel)
                return
            
            return None


        if message.content.startswith('!untrack'):
            # Check if the user is registered
            # Check if the user input is correct
            # Check if the item is alredy tracking

            user = message.author
            user_discord_id = message.author.id
            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await self.message_user(user_discord_id, need_registration, message.channel)
                return
                
            
            # correct usage:  !untrack item_id/item_name
            # example         !untrack 21018


            search_term = await bot_helper.parse_track_command(message.content)

            if (search_term is None):
         
                invalid_format_response = "Example Usage is: \n !untrack item_id\n !untrack 21018"
                invalid_tracking_input = discord.Embed(title=search_term, description=invalid_format_response, color=warning_color)
                await self.message_user(user_discord_id, invalid_tracking_input, message.channel)
                return

            item_id = None
            item_name = None

            # user type in item_id
            if search_term.isdigit():

                item_id = search_term
                item_name = bot_helper.get_item_name(item_id)

                if (item_name == "Unknown"):
                    no_result_respond = discord.Embed(title="No item found", description="There is no item with ID " + search_term, color=warning_color)
                    await self.message_user(user_discord_id, no_result_respond, message.channel)
                    return

            # user type in item_name
            else:

                try:
                    search_matches = bot_helper.search_item(search_term)
                    
                except Exception as e:
                    
                    nova_down_respond = discord.Embed(title="Cannot Connect to Nova at the Moment", description="Please try again some other time", color=error_color)
                    await self.message_user(user_discord_id, nova_down_respond, message.channel)
                    return

                                
                if search_matches is None:
                    no_result_respond = discord.Embed(title="No item found", description="There is no search result for " + search_term + ", try using item id", color=warning_color)
                    await self.message_user(user_discord_id, no_result_respond, message.channel)
                    return


                ### PROMPT for selection/ item_id /item_name

                index = 0
                
                if len(search_matches) > 1:


                    select_item = discord.Embed(title="Please __**Enter the index**__ to select the item, type anything else to dismiss", description=str(len(search_matches)) + " results", color=feedback_color)

                    count = 0
                    for match in search_matches:
                        count += 1
                        select_item.add_field(name="Index: " + str(count), value="**" + match[0] + "** (" + match[1] + ")", inline=False)
                        
                    await self.message_user(user_discord_id, select_item, message.channel)

                    # Get user input
                    try:
                        user_input_index = await client.wait_for('message', check = lambda message: message.author == user, timeout=120.0)
                    except asyncio.TimeoutError:
                        dismiss_select = discord.Embed(title="Dismiss", description="Automatically dismiss after 2 minutes", color=warning_color)
                        await self.message_user(user_discord_id, dismiss_select, message.channel)
                        return
                    
                    try:

                        user_input_index = int(user_input_index.content)
                        if (user_input_index < 1 or user_input_index > count):
                            raise Exception("Invalid Index")
                        index = user_input_index -1
                        
                        
                    except Exception as e:
                        dismiss_select = discord.Embed(title="Dismiss", description=str(e), color=warning_color)
                        await self.message_user(user_discord_id, dismiss_select, message.channel)
                        return
                    
                item_id = search_matches[index][1]
                item_name = search_matches[index][0]


            if not (await bot_helper.already_tracking(user_discord_id, item_id)):

                not_tracking_response = "You have not been tracking " + "**" +item_name + "**" + " (" + item_id + ")"
                not_tracking = discord.Embed(title="Untrack Fail", description=not_tracking_response, color=warning_color)                
                await self.message_user(user_discord_id, not_tracking, message.channel)
                return

            try:
                await bot_helper.user_untrack_item(user_discord_id, item_id)

                untrack_success_response = "You are no longer tracking " + "**" + item_name + "**" + " (" + item_id + ")"
                untrack_success = discord.Embed(title="Untrack Success", description=untrack_success_response, color=success_color)                
                await self.message_user(user_discord_id, untrack_success, message.channel)
                
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await self.message_user(user_discord_id, crash, message.channel)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)

            return None


        if message.content.startswith('!clear'):

            user_discord_id = message.author.id

            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await self.message_user(user_discord_id, need_registration, message.channel)
                return


            try:
                tracking_items = await bot_helper.untrack_all(user_discord_id)

            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await self.message_user(user_discord_id, crash, message.channel)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)


            if (tracking_items == []):
                nothing_on_track = discord.Embed(title="No items tracking", description="You are currently not tracking any item", color=feedback_color) 
                await self.message_user(user_discord_id, nothing_on_track, message.channel)
                return


            for item_id, item_name in tracking_items:

                untrack_success_response = "You are no longer tracking " + "**" + item_name + "**" + " (" + item_id + ")"
                untrack_success = discord.Embed(title="Untrack Success", description=untrack_success_response, color=success_color)                
                await self.message_user(user_discord_id, untrack_success, message.channel)
                
                
            return None
    
        if message.content.startswith('!lowest'):

            user_discord_id = message.author.id

            if not(await bot_helper.already_registrated(user_discord_id)):
                need_registration = discord.Embed(title="Need Registration", description="Please register with !register command", color=error_color) 
                await self.message_user(user_discord_id, need_registration, message.channel)
                return
                
            try:
                lowest_report = await bot_helper.get_lowest(user_discord_id)
            except Exception as e:
                crash = discord.Embed(title=crash_title, description=str(message.author.id) +"\n"+ traceback.format_exc(), color=error_color) 
                await self.message_user(user_discord_id, crash, message.channel)
                await client.get_user(MY_DISCORD_ID).send(embed=crash)
                return

            if (lowest_report == []):
                nothing_on_track = discord.Embed(title="No items tracking", description="You are currently not tracking any item", color=feedback_color) 
                await self.message_user(user_discord_id, nothing_on_track, message.channel)
                return

            for result in lowest_report:
                await self.notify_user(user_discord_id,result, message.channel)

            return None


        if message.content.startswith('!run') and message.author.id == MY_DISCORD_ID:
            self.show_run = not self.show_run

            run_status = "Showing notify cycle" if self.show_run else "Hiding notify cycle" 
            set_show_run = discord.Embed(title="Cycle status", description=run_status, color=success_color) 
            await client.get_user(MY_DISCORD_ID).send(embed=set_show_run) 
            


        if message.content.startswith('!help'):

            user_discord_id = message.author.id

            embed=discord.Embed(title="NovaTracker Commands", description="Please support this bot by telling your friends!", color=feedback_color)
            embed.add_field(name="!start", value="Give a brief description of this bot for first time user", inline=False)
            embed.add_field(name="!about", value="Display user number and bot status", inline=False)
            embed.add_field(name="!doc", value="Disply link to github documentation", inline=False)
            embed.add_field(name="!register", value="Initialize user in the database, this registration is bond to the user's discord id", inline=False)
            embed.add_field(name="!track [name/id]", value="**Where the fun begin!**", inline=False)
            embed.add_field(name="!untrack [name/id]", value="Stop tracking the item", inline=False)
            embed.add_field(name="!clear", value="Untrack all items at once", inline=False)
            embed.add_field(name="!showtrack", value="List all the items user is currently tracking", inline=False)
            embed.add_field(name="!lowest", value="Display the lowest price of the tracking items currently on market", inline=False)
            embed.add_field(name="!contact", value="Feel free to reach out to me", inline=False)
            embed.add_field(name="!quote", value="Show one of my favourite quote", inline=False)
            embed.add_field(name="!help", value="List all the commands for this bot", inline=False)
        
            await self.message_user(user_discord_id, embed, message.channel)
            

            return

           


        if message.content.startswith('!start'):

            user_discord_id = message.author.id

            bot_description = "Nova Tracker is a discord bot to help user track items on sell in the Nova market\n"
            bot_description += "It personalizes your tracking preference and notifies you directly on discord\n"
            bot_description += "This bot handles all messages directly so just pm it like a discord user\n"
            bot_description += "Do notice that if Nova website is down this bot will also be down\n"
            bot_description += "**This bot must need your permission to allow private dm, otherwise it cannot notify you and will delete you as a user!**\n"
            bot_description += "inside your discord setting-> privacy & safety-> Turn ON Allow direct message from server member\n"
     
            start_message = discord.Embed(title="Start using NovaTracker", description=bot_description, color=feedback_color)                
            await self.message_user(user_discord_id, start_message, message.channel)
            
        # For fun stuff all here======================================
    
        if message.content.startswith('!about'):

            user_discord_id = message.author.id

            user_numbers = bot_helper.get_user_number()

            about_text = "Currently on Version {} ".format(version)
            about_text += "with " + "**"+str(user_numbers)+ "**" + " users\n"
            about_text += "Thank you for using NovaTracker\n"
            about_text += "Please support this bot by telling your friends!"
            about_message = discord.Embed(title="Made with Babyish Love", description=about_text, color=feedback_color)                
            await self.message_user(user_discord_id, about_message, message.channel)

        if message.content.startswith('!quote'):

            user_discord_id = message.author.id
            quote = discord.Embed(title=self.q.get_random_quote(), color=feedback_color)                
            await self.message_user(user_discord_id, quote, message.channel)

        if message.content.startswith('!doc'):

            user_discord_id = message.author.id
            doc_link = discord.Embed(title="Github Documentation", description=DOC_LINK, color=feedback_color)                
            await self.message_user(user_discord_id, doc_link, message.channel)
            
        if message.content.startswith('!contact'):

            user_discord_id = message.author.id
            contact_info = discord.Embed(title="Contact Info", description=MY_DISCORD_NAME, color=feedback_color)                
            await self.message_user(user_discord_id, contact_info, message.channel)


    async def delete_user(self, user_id):

        if (await bot_helper.already_registrated(user_id)):

            await bot_helper.remove_user(user_id)
            print("Deleted user :" + str(user_id))
            delete_user_report = discord.Embed(title="Delete Invalid User", description="Deleted invalid user :" + str(user_id), color=feedback_color) 
            await client.get_user(MY_DISCORD_ID).send(embed=delete_user_report)
            
        return
        
    #safe guard function in case user become not valid or turned off dm permission
    async def message_user(self, user_id, embedded_message, channel = None):

        user = client.get_user(user_id)

        # not user can get pass in from notify_user having multiple messages and already delete the user in the first message
        if (await bot_helper.already_registrated(user_id)):

            if (user is None):
                # if user id is invalid, may be due to delete discord account
                await self.delete_user(user.id)

            try:
                # try to DM first...

                await user.send(embed=embedded_message)

            # user disable private dm and not come from a channel, delete user
            except discord.errors.Forbidden:

                # if message comes from a channel, reply back to channel
                if (channel is not None):
                    await channel.send(embed=embedded_message)

                    # give them a warning... for no allowing DM
                    need_dmp = "**This bot must need your permission to allow private dm, otherwise it cannot notify you and will delete you as a user!**\n"
                    need_dmp += "inside your discord setting-> privacy & safety-> Turn ON Allow direct message from server member\n"
                    needDM = discord.Embed(title="Warning", description=need_dmp, color=warning_color)                
                    await channel.send(embed=needDM)
                    
                else:
                # no channel, delete this user

                    cannot_notify_report = discord.Embed(title="Cannot message user", description= str(user_id), color=feedback_color) 
                    await client.get_user(MY_DISCORD_ID).send(embed=cannot_notify_report)
                    await self.delete_user(user_id)
        return
    
    async def notify_user(self, user_id, notify_message, channel = None):
        # channel will be None if it is pass from cycle, not None if pass from !lowest
 
        onsell_notification = discord.Embed(title="Item on sell", description=notify_message, color=notify_color)
        await self.message_user(user_id, onsell_notification, channel)
            
    async def track_nova_market(self):

        await self.wait_until_ready()
        
        while not client.is_closed():
            
            await asyncio.sleep(900) # 900s = run every 15 minutes
            
            now = datetime.now(tz=pytz.utc)
            start_time = now.astimezone(timezone('US/Pacific'))
            print("Starting cycle at " + start_time.strftime("%Y-%m-%d %H:%M %p"))
            s = time.time()
            
            # get the market data
            try: 
                loop = asyncio.get_event_loop()
                to_notify = await loop.run_in_executor(ThreadPoolExecutor(), bot_helper.handle_user_trackings)
                print("Obtaining market info took {:.2f}s".format((time.time() - s)))


                # notify users, disable in developement
                for user_id, message in to_notify:
                    await self.notify_user(user_id,message)


            except Exception as e:
                now = datetime.now(tz=pytz.utc)
                problem_time = now.astimezone(timezone('US/Pacific'))
                print("Problem in cycle at " + problem_time.strftime("%Y-%m-%d %H:%M %p"))
                print(traceback.format_exc())
                crash_title_for_me = "Problem in cycle at " + now.strftime("%Y-%m-%d %H:%M %p")
                crash = discord.Embed(title=crash_title_for_me, description=traceback.format_exc(), color=error_color) 
                await client.get_user(MY_DISCORD_ID).send(embed=crash)


            now = datetime.now(tz=pytz.utc)
            end_time = now.astimezone(timezone('US/Pacific'))
            run_info = "Complete cycle at " + end_time.strftime("%Y-%m-%d %H:%M %p") + ", execution time is {:.2f}s".format(time.time() - s)
            print(run_info)
            
            if (self.show_run):
                running_proof = discord.Embed(title="Running", description=run_info, color=success_color) 
                await client.get_user(MY_DISCORD_ID).send(embed=running_proof) 
        return



client = MyClient()
client.run(DISCORD_TOKEN)

#DISCORD_TOKEN_DEV, DISCORD_TOKEN
# make sure to disable notification when using DISCORD_TOKEN_DEV

