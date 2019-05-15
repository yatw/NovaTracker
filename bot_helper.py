import asyncio
import discord
import re

from discord.ext import commands
from bot_config import db
import novamarket


# Get user_number ======================================================================================

def get_user_number():
    return db.users.count_documents({})

# information Functions ================================================================================
# both might need nova connection

def can_refine(item_id):
    '''First look through database, if not found, check nova website'''

    result = db.items.find_one({'ITEM_ID' : item_id})


    # if database has this item, just return the stored variable
    if (result is not None):
        return result['REFINABLE']

    # if database don't have, check nova website
    return novamarket.can_refine(item_id)

def get_item_name(item_id):
    '''First look through database, if not found, check nova website'''


    result = db.items.find_one({'ITEM_ID' : item_id})


    # if database has this item, just return the stored name
    if (result is not None):
        return result['ITEM_NAME']

    # if database don't have, check nova website
    return novamarket.search_item_name(item_id)



# Text formatting functions all here =======================================================================
def price_format(price):
    # 3500000 to 3,500,000z

    return str('{:,}'.format(price)) + 'z'


def to_price(price):

    return price.lower().replace("k","000").replace("m","000000").replace("b","000000000")


def construct_notification_message(item_name, item_id, refinable, refine_level, price, location):

    notification_message  = "**" + item_name

    if (refinable):
        notification_message += " +" + refine_level
        
    notification_message += "**" + " (" + item_id + ")" 
    notification_message += " is on sell " +  "**" + price_format(price) +  "**"
    notification_message += " at " +  "**" + location + "**" 

    return notification_message


# Handle Register related functions ========================================================================

async def already_registrated(user_discord_id):
    '''Return True if find user in the database'''

    return db.users.find_one({'DISCORD_ID' : user_discord_id}) is not None

async def user_register(user_discord_id):
    
    db.users.insert_one(
        {
            'DISCORD_ID' : user_discord_id,
            'INTERESTED_ITEMS' : {}
        }
    )

    return None

# Handle Remove User ======================================================================================

async def remove_user(user_discord_id):

    # first find all the item this user is tracking
    # call untrack on all of them
    # remove this user

    tracking_items = db.users.find_one({'DISCORD_ID' : user_discord_id})['INTERESTED_ITEMS']

    for item_id in tracking_items:

        remove_tracking_users(user_discord_id, item_id)
    
    db.users.delete_one({'DISCORD_ID' : user_discord_id})


    return None


# Show track function =====================================================================================

async def show_tracking_items(user_discord_id):


    tracking_message = ""
    tracking_items = db.users.find_one({'DISCORD_ID' : user_discord_id})['INTERESTED_ITEMS']

    count = 0
    for item_id in tracking_items:
        count += 1
        tracking_message += str(count) + ": " + "**"+ get_item_name(item_id) +"**"+ " " + "(" + item_id + ")" + "\t"
        tracking_message += "refine >= " + "**"+str(tracking_items[item_id]['REFINE_GOAL'])+"**"
        tracking_message += " ,sell price <= " + "**"+price_format(tracking_items[item_id]['IDEAL_PRICE'])+ "**" + "\n"

    return tracking_message


# Handle Track functions ===================================================================================

async def already_tracking(user_discord_id, item_id):

    return item_id in db.users.find_one({'DISCORD_ID' : user_discord_id})['INTERESTED_ITEMS']

async def count_tracking_item(user_discord_id):

    return len(db.users.find_one({'DISCORD_ID': user_discord_id})['INTERESTED_ITEMS'])


async def parse_track_command(command):
    # correct usage:  !track item_id refine_goal ideal_price(K,M,B all work)
    # example         !track 21018 8 200m


    result = {}
    try:
        tokens = re.findall(r"[A-Za-z0-9]+",command)

        if (len(tokens) > 4):
            raise Exception('Extra tokens')
        elif (len(tokens) < 4):
            raise Exception('Missing tokens')

        # CHECK if item in database, if so, get item name and refinable, else ping nova

        item_id = tokens[1]

        item_name = get_item_name(item_id) # get_item_name can fail if Nova is down
        if (item_name == "Unknown"):
            raise Exception('Invalid Item ID')


        # if refine able check if refine is valid 
        refine_goal = int(tokens[2])
        if (refine_goal < 0 or refine_goal > 20):
            raise Exception('Valid refine is 0 to 20')
        result["refine_goal"] = refine_goal
       
        refinable = can_refine(item_id) # can_refine can fail if Nova is down
        if not (refinable):
            result["refine_goal"] = 0
        result["refinable"] = refinable


        ideal_price = int(to_price(tokens[3]))
        if (ideal_price < 1 or ideal_price > 1000000000):
            raise Exception('Valid price range is 1 to 1,000,000,000')
        result["ideal_price"] = ideal_price            

        result["item_id"] = item_id
        result["item_name"] = item_name
        
        result["invalid"] = False
    except Exception as e:
        result["invalid"] = True
        result["problem"] = str(e)
        

    return result


async def user_track_item(user_discord_id, item_id, item_name, ideal_price, refinable, refine_goal):

    # insert item into users collection

    user_interested_items = db.users.find_one({'DISCORD_ID' : user_discord_id})['INTERESTED_ITEMS']

    user_item_preference = {

            'IDEAL_PRICE': ideal_price,
            'REFINE_GOAL': refine_goal
    }

    user_interested_items[item_id] = user_item_preference
    
    db.users.update_one(
        {'DISCORD_ID' : user_discord_id},
        {'$set': {'INTERESTED_ITEMS': user_interested_items}}
    )

    # Adding new item into the database
    # generate document for each refine level

    # if this item not yet in the database, record this item
    if db.items.find_one({'ITEM_ID' : item_id}) is None:

        REFINE_DICT = generate_refine_dict(refinable)
        item_info = {

                'ITEM_ID': item_id,
                'ITEM_NAME': item_name,
                'REFINABLE': refinable,
                'REFINE' : REFINE_DICT
        }
        
        db.items.insert(item_info)

    # put user into this item's notify list, every refine level
    insert_tracking_users(user_discord_id,item_id, refinable, refine_goal)
        
    return None
    
def generate_refine_dict(refinable):

    REFINE_DICT = {}
    refine_limit = 0
    
    if (refinable):
        refine_limit = 20
    
    for refine_level in range(0,refine_limit+1):

        REFINE_DICT[str(refine_level)] = []

    return REFINE_DICT

def insert_tracking_users(user_discord_id, item_id, refinable, refine_goal):

    keep_track_to = 20

    # if this item not refinable, just put in level 0
    if (not refinable):
        refine_goal = 0
        keep_track_to = 0

    # other refineable items, put from user_refine goal to 20
    for refine_level in range(refine_goal,keep_track_to+1):

        REFINE_DICT = db.items.find_one({'ITEM_ID' : item_id})['REFINE']

        REFINE_DICT[str(refine_level)].append(user_discord_id)
    
        db.items.update_one(
            {
                'ITEM_ID' : item_id,
            },
            {
                '$set': {'REFINE' : REFINE_DICT}
            }
            
        )
        
    return None



# Handle Untrack commands functions===============================================================================

async def parse_untrack_command(command):
    # all you have to do is vertify the item_id is valid, but doesn't check if it exist
    # correct usage:  !untrack item_id
    # example         !untrack 21018

    result = {}
    try:
        tokens = re.findall(r"[A-Za-z0-9]+",command)

        if (len(tokens) > 2):
            raise Exception('Extra tokens')
        elif (len(tokens) < 2):
            raise Exception('Missing tokens')

        item_id = tokens[1]

        item_name = get_item_name(item_id)
        if item_name == "Unknown":
            raise Exception('Item Not Found')
    
        result["item_id"] = item_id
        result["item_name"] = item_name
        result["invalid"] = False
        return result

    except Exception as e:
        result["invalid"] = True
        result["problem"] = str(e)
        return result


    return result


async def user_untrack_item(user_discord_id, item_id):

    # remove the user from the item's notify list, every level
    remove_tracking_users(user_discord_id, item_id)

    user_interested_items = db.users.find_one({'DISCORD_ID' : user_discord_id})['INTERESTED_ITEMS']
    user_interested_items.pop(item_id, None);
    
    db.users.update_one(
        {'DISCORD_ID' : user_discord_id},
        { '$set': {'INTERESTED_ITEMS': user_interested_items}}
    )

    return None


def remove_tracking_users(user_discord_id, item_id):

    # remove user from item's notify list, for every refine level

    user = db.users.find_one({'DISCORD_ID': user_discord_id})
    refine_goal = user['INTERESTED_ITEMS'][item_id]['REFINE_GOAL']
    
    refine_limit = 20

    if (not db.items.find_one( {'ITEM_ID': item_id})['REFINABLE']):
        refine_limit = 0

    for refine_level in range(refine_goal, refine_limit+1):


        REFINE_DICT = db.items.find_one({'ITEM_ID' : item_id})['REFINE']

        REFINE_DICT[str(refine_level)].remove(user_discord_id)

        db.items.update(
            {
                'ITEM_ID' : item_id,
            },
            {
                '$set': {'REFINE' : REFINE_DICT}
            }
            
        )

    return None


# Repeat notifying function==================================================================================

def handle_user_trackings():

    # get all the items in the database
    # check nova market
    # get all the tracking users for each refine level
    # notify user if there is a match


    to_notify = []

    for item in db.items.find():


        # if no one is tracking this item, we can just skip pining Nova
        if (no_one_tracking(item['REFINE'])):
            continue
        
                
        on_sell = novamarket.current_market_info(item['ITEM_ID'])

        # No item on sell at all (mvp card)
        if (on_sell is None):
            continue

        refinable = item['REFINABLE']

        # for every refine_level
        for refine_level in item['REFINE']:

            if (on_sell[refine_level]['price'] == -1): #refine of this level not on sell
                continue

            lowest_price = on_sell[refine_level]['price']
            location = on_sell[refine_level]['location']

            # check for all user in that refine level
            for tracking_user in item['REFINE'][refine_level]:

                # check user onsell price <= ideal price
                
                ideal_price = db.users.find_one({'DISCORD_ID' : tracking_user})['INTERESTED_ITEMS'][item['ITEM_ID']]['IDEAL_PRICE']
             
                if lowest_price <= ideal_price:
                    message = construct_notification_message(item['ITEM_NAME'], item['ITEM_ID'], refinable, refine_level, lowest_price, location)
                    to_notify.append((tracking_user,message))

              
    return to_notify

def no_one_tracking(refine_level_list):

    for refine_level in refine_level_list:
        if len(refine_level) > 0:
            return False

    # all refine level is empty
    return True

