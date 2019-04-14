import asyncio
import discord
import re

from discord.ext import commands
from bot_config import db
import novamarket


def price_format(price):
    # 3500000 to 3,500,000z

    return str('{:,}'.format(price)) + 'z'


def to_price(price):

    return price.lower().replace("k","000").replace("m","000000").replace("b","000000000")


def construct_notification_message(name, refine_level, price, location):

    return name + " " + "+"+refine_level + " is on sell " + price_format(price) + " at " + location



def handle_user_trackings():

    # get all the items in the database
    # check nova market
    # get all the tracking users for each refine level
    # notify user if there is a match


    to_notify = []

    for item in db.items.find():
                
        on_sell = novamarket.current_market_info(item['ITEM_ID'])

        # No item on sell at all (mvp card)
        if (on_sell is None):
            continue

        # for every refine_level
        for data_at_level in item['REFINE']:

            refine_level = str(data_at_level['REFINE_LEVEL'])

            if (on_sell[refine_level]['price'] == -1): #refine of this level not on sell
                continue

            lowest_price = on_sell[refine_level]['price']
            location = on_sell[refine_level]['location']

            # check for all user in that refine level
            for user in data_at_level['TRACKING_USERS']:

                # check user onsell price <= ideal price
                
                user_record = db.users.find_one(

                    {'DISCORD_ID' : user,
                    'INTERESTED_ITEMS': {'$elemMatch':{'ITEM_ID': item['ITEM_ID']}}}
    
                )
                for item_track in user_record['INTERESTED_ITEMS']:

                    if (item_track['ITEM_ID'] == item['ITEM_ID']):
                    
                        ideal_price = item_track['IDEAL_PRICE']
   
                        if lowest_price <= ideal_price:
                            message = construct_notification_message(item['ITEM_NAME'], refine_level, lowest_price, location)
                            to_notify.append((user,message))

              
    return to_notify

async def vertify_track_command(command):
    # correct usage:  !track item_id refine_goal ideal_price(K,M,B all work)
    # example         !track 21018 8 200m


    result = {}
    try:
        tokens = re.findall(r"[A-Za-z0-9]+",command)

        if (len(tokens) > 4):
            raise Exception('Extra parameters')

        # CHECK if item in database, if so, get item name and refinable, else ping nova

        item_id = tokens[1]

        item_name = get_item_name(item_id)
        if (item_name == "Unknown"):
            raise Exception('Invalid Item ID')


        # if refine able check if refine is valid 
        refine_goal = int(tokens[2])
        if (refine_goal < 0 or refine_goal > 20):
            raise Exception('Invalid Refine Goal')
        result["refine_goal"] = refine_goal
       
        refinable = can_refine(item_id)
        if not (refinable):
            result["refine_goal"] = 0
        result["refinable"] = refinable


        ideal_price = int(to_price(tokens[3]))
        if (ideal_price < 0 or ideal_price > 1000000000):
            raise Exception('Invalid Ideal Price')
        result["ideal_price"] = ideal_price            

        result["item_id"] = item_id
        result["item_name"] = item_name
        
        result["invalid"] = False
    except:
        result["invalid"] = True

    return result


async def show_tracking_items(user_discord_id):


    tracking_message = ""
    tracking_items = db.users.find_one({'DISCORD_ID' : user_discord_id})['INTERESTED_ITEMS']

    count = 0
    for t in tracking_items:
        count += 1
        tracking_message += str(count) + ": " + get_item_name(t['ITEM_ID']) + " " + t['ITEM_ID'] + "\t" + "refine >= " + str(t['REFINE_GOAL']) + " ,at <= " + price_format(t['IDEAL_PRICE']) + "\n"

    return tracking_message

async def already_registrated(user_discord_id):
    '''Return True if find user in the database'''


    if (db.users.find({'DISCORD_ID' : user_discord_id}).count() != 0):
        return True

    return False

async def user_register(user_discord_id):
    
    db.users.insert(
        {
            'DISCORD_ID' : user_discord_id,
            'INTERESTED_ITEMS' : []
        }
    )

    return None


async def already_tracking(user_discord_id, item_id):

    return db.users.find(

            {'DISCORD_ID' : user_discord_id,
            'INTERESTED_ITEMS': {'$elemMatch':{'ITEM_ID': item_id}}}
    
    ).count() == 1


async def vertify_untrack_command(command):
    # all you have to do is vertify the item_id is valid, but doesn't check if it exist
    # correct usage:  !untrack item_id
    # example         !untrack 21018

    try:
        result = re.findall(r"[A-Za-z0-9]+",command)

        if (len(result) > 2):
            raise Exception('Extra parameters')

        int(result[1]) # check that it is int
        return result[1]

    except:
        return ""


    return ""


async def count_tracking_item(user_discord_id):

    return len(db.users.find_one({'DISCORD_ID': user_discord_id})['INTERESTED_ITEMS'])

async def user_track_item(user_discord_id, item_id, item_name, ideal_price, refinable, refine_goal):

    # insert item into users collection

    user_item_info = {

            'ITEM_ID': item_id,
            'IDEAL_PRICE': ideal_price,
            'REFINE_GOAL': refine_goal
    }
    
    db.users.update(
        {'DISCORD_ID' : user_discord_id},
        {'$push': {'INTERESTED_ITEMS': user_item_info}}
    )

    # Adding new item into the database
    # generate document for each refine level

    # if this item not yet in the database, record this item
    if db.items.find({'ITEM_ID' : item_id}).count() == 0:

        REFINE_LIST = generate_refine_list(refinable)
        item_info = {

                'ITEM_ID': item_id,
                'ITEM_NAME': item_name,
                'REFINABLE': refinable,
                'REFINE' : REFINE_LIST
        }
        
        db.items.insert(item_info)

    insert_tracking_users(user_discord_id,item_id, refinable, refine_goal)
        
    return None
    

def generate_refine_list(refinable):

    REFINE_LIST = []
    refine_limit = 0
    
    if (refinable):
        refine_limit = 20
    
    for refine_level in range(0,refine_limit+1):

        REFINE_LIST.append(

            {'REFINE_LEVEL': refine_level,
             'TRACKING_USERS': []
             }
        )

    return REFINE_LIST

def insert_tracking_users(user_discord_id, item_id, refinable, refine_goal):

    keep_track_to = 20

    # if this item not refinable, just put in level 0
    if (not refinable):
        refine_goal = 0
        keep_track_to = 0

    # other refineable items, put from user_refine goal to 20
    for refine_level in range(refine_goal,keep_track_to+1):

        db.items.update(
            {
                'ITEM_ID' : item_id,
                'REFINE.REFINE_LEVEL' : refine_level
            },
            {
                '$push': {'REFINE.$.TRACKING_USERS' : user_discord_id}
            }
            
        )
        
    return None

def remove_tracking_users(user_discord_id, item_id):

    user = db.users.find_one(

        {'DISCORD_ID': user_discord_id,
         'INTERESTED_ITEMS': {'$elemMatch': { 'ITEM_ID': item_id}}
        }
    )
    refine_goal = user['INTERESTED_ITEMS'][0]['REFINE_GOAL']
    refine_limit = 20

    if (not db.items.find_one( {'ITEM_ID': item_id})['REFINABLE']):
        refine_limit = 0

    for refine_level in range(refine_goal, refine_limit+1):

        db.items.update(
            {
                'ITEM_ID' : item_id,
                'REFINE.REFINE_LEVEL' : refine_level
            },
            {
                '$pull': {'REFINE.$.TRACKING_USERS' : user_discord_id}
            }
            
        )
    return None

 
async def user_untrack_item(user_discord_id, item_id):


    remove_tracking_users(user_discord_id, item_id)

    db.users.update(
        {'DISCORD_ID' : user_discord_id},
        { '$pull': {'INTERESTED_ITEMS': {'ITEM_ID' : item_id}}}
    )

    return None

def can_refine(item_id):
    '''First look through database, if not found, check nova website'''

    result = db.items.find_one({'ITEM_ID' : item_id})


    # if database has this item, just return the stored name
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

