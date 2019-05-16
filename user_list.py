from bot_config import db


# A simple script to see what user is tracking what

count = 1
for user in  db.users.find():

    print(count)
    for item in user["INTERESTED_ITEMS"]:


        refine_goal = (user["INTERESTED_ITEMS"][item]["REFINE_GOAL"])


        print(str(user["DISCORD_ID"]) + " is tracking " + item + " at +" + str(refine_goal))


        item_db = db.items.find_one({"ITEM_ID": item})
        
        for refine_level in item_db["REFINE"]:

            if int(refine_level) >= int(refine_goal):

                if user["DISCORD_ID"] not in item_db["REFINE"][refine_level]:
                    print(str(user["DISCORD_ID"]) + " not in " + item + " "+ refine_level)
        
    print("======")
    count += 1



'''
user_interested_items = db.users.find_one({'DISCORD_ID' : asdklfjlask})['INTERESTED_ITEMS']
user_interested_items.pop("6671", None);

db.users.update_one(
    {'DISCORD_ID' : sadfjlkadsjflk},
    { '$set': {'INTERESTED_ITEMS': user_interested_items}}
)
'''



