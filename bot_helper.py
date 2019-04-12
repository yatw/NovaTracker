import asyncio
import discord
import re

from discord.ext import commands
from bot_config import db
import novamarket



def handle_user_trackings():

    # get all the items in the database
    # check nova market
    # get all the tracking users for each refine level
    # notify user if there is a match

    for item in db.items.find():
        print(item['ITEM_NAME'])
        novamarket.current_market_info(item['ITEM_ID'])




        
    return None


async def vertify_track_command(command):
    # correct usage:  !track item_id refine_goal ideal_price(K,M,B all work)
    # example         !track 21018 8 200m

    try:
        result = re.findall(r"[A-Za-z0-9]+",command)

        if (len(result) >= 5):
            raise Exception('Extra parameters')

        item_id = result[1]

        #TODO get item name and item class(refinable) in here
        item_name = get_item_name(item_id)
        if (item_name == "Unknown"):
            raise Exception('Invalid Item ID')


        # if refine able check if refine is valid 
        refine_goal = int(result[2])
        if (refine_goal < 0 or refine_goal > 20):
            raise Exception('Invalid Refine Goal')
        result[2] = refine_goal
       

        ideal_price = int(to_price(result[3]))
        if (ideal_price < 0 or ideal_price > 1000000000):
            raise Exception('Invalid Ideal Price')
        result[3] = ideal_price            


        
        result.append(item_name)
        
        result[0] = 1 # valid
    except:
        result[0] = 0 # not valid

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

        if (len(result) >= 3):
            raise Exception('Extra parameters')

        int(result[1]) # check that it is int
        return result[1]

    except:
        return ""


    return ""



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
             'LOWEST_PRICE' : -1,
             'SELLING_LOCATION' : "",
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
    return novamarket.can_refine(item_id)

def get_item_name(item_id):
    '''First look through database, if not found, check nova website'''


    result = db.items.find_one({'ITEM_ID' : item_id})


    # if database has this item, just return the stored name
    if (result is not None):
        return result['ITEM_NAME']

    # if database don't have, check nova website
    return novamarket.search_item_name(item_id)

def price_format(price):
    # 3500000 to 3,500,000z

    return str('{:,}'.format(price)) + 'z'


def to_price(price):

    return price.lower().replace("k","000").replace("m","000000").replace("b","000000000")


