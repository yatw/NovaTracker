import os
import asyncio
import atexit
import discord
import flask
import threading


from apscheduler.schedulers.background import BackgroundScheduler
from config import MY_PHONE_NUMBER, TWILIO_PHONE_NUMBER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TEST_TWILIO_ACCOUNT_SID, TEST_TWILIO_AUTH_TOKEN, FIREBASE_URL
from config import db
from flask import Flask, render_template, request
#from firebase import firebase
from novamarket import check_nova_market
from trackerbot import MyClient
from twilio.rest import Client


app = Flask(__name__)


@app.route("/add")
def add():

    user_info = {

            'DISCORD_ID' : '294974177184579585',
            'INTERESTED_ITEMS':[
                {
                    'ITEM_ID':'15147',
                    'REFINE_REQ': 8
                },
                {
                    'ITEM_ID':'15146',
                    'REFINE_REQ': 8
                }
                ]
        }

    
    db.users.insert(user_info)
    return 'Added User!'

@app.route("/", methods=['GET', 'POST'])
def index():

    
     



    get_users()
    '''

    scheduler = BackgroundScheduler({'apscheduler.timezone': 'America/Los_Angeles'})
    scheduler.start()
    scheduler.add_job(func=check_market, trigger="interval", seconds=10)
    atexit.register(lambda: scheduler.shutdown())
    '''
    return render_template("index.html")


def get_users():

    print(db.users)
        

def check_market():

    
    tracking = get_tracking_items()

    item_interested = tracking['item_id']
    ideal_price = tracking['ideal_price']
    refine_goal = tracking['refine_goal']

    result = check_nova_market(item_id = item_interested,
                      refine_goal = refine_goal,
                      ideal_price = ideal_price,
                      )

    print(result)
    
    if (len(result) > 0):
        # do something
        print()
    
    return None

    

def get_tracking_items():

    #fire = firebase.FirebaseApplication(FIREBASE_URL, None)
    #result = fire.get('/'+ MY_GAME_NAME, None)





    
    return result['item']


def notify_user_message(result):

    item_info = "Nova Market"

    client = Client(TEST_TWILIO_ACCOUNT_SID,TEST_TWILIO_AUTH_TOKEN)

    message = client.messages.create(to=MY_PHONE_NUMBER, from_=TWILIO_PHONE_NUMBER,
                                     body=item_info)
    
    return None



if __name__ == "__main__":

    
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
