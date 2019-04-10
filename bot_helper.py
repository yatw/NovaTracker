import asyncio
import discord
import re

from discord.ext import commands
from bot_config import db
import novamarket


async def vertify_track_command(command):
    # correct usage:  !track item_id ideal_price refine_goal
    # example         !track 21018 800000000 8

    try:
        result = re.findall(r"[A-Za-z0-9]+",command)

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
        result = re.findall(r"[\w]+",command)

        if (len(result) >= 3):
            raise Exception('Extra parameters')

        int(result[1]) # check that it is int
        return result[1]

    except:
        return ""


    return ""



async def user_track_item(user_discord_id, item_id, item_name, ideal_price, refine_goal):


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


    item_search = {
        'ITEM_ID' : item_id,
        'REFINE': refine_goal
    }

    
    if db.items.find(item_search).count() == 0:


        item_info = {

                'ITEM_ID': item_id,
                'ITEM_NAME': item_name,
                'REFINE' : refine_goal,
                'LOWEST_PRICE': -1,
                'TRACKING_USERS': [user_discord_id]
    
        }
        
        db.items.insert(item_info)
        
    else:

        db.items.update(
            {'ITEM_ID' : item_id,
             'REFINE' : refine_goal
            },
            {'$push': {'TRACKING_USERS': user_discord_id}}
        )
 
   
    return None


async def user_untrack_item(user_discord_id, item_id):

    db.users.update(
        {'DISCORD_ID' : user_discord_id},
        { '$pull': {'INTERESTED_ITEMS': {'ITEM_ID' : item_id}}}
    )

    return None


def get_item_name(item_id):
    '''First look through database, if not found, check nova website'''


    result = db.items.find_one({'ITEM_ID' : item_id})


    # if database has this item, just return the stored name
    if (result is not None):
        return result['ITEM_NAME']

    # if database don't have, check nova websitee
    return novamarket.search_item_name(item_id)


    

