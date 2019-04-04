import os
import atexit
import flask

from apscheduler.schedulers.background import BackgroundScheduler
from config import MY_PHONE_NUMBER, TWILIO_PHONE_NUMBER, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TEST_TWILIO_ACCOUNT_SID, TEST_TWILIO_AUTH_TOKEN, FIREBASE_URL
from flask import Flask, render_template, request
from firebase import firebase
from novamarket import check_nova_market
from twilio.rest import Client


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():

    scheduler = BackgroundScheduler({'apscheduler.timezone': 'America/Los_Angeles'})
    scheduler.start()
    scheduler.add_job(func=check_market, trigger="interval", seconds=10)
    atexit.register(lambda: scheduler.shutdown())

    return "sub"

def check_market():


    tracking = get_tracking_items()

    item_interested = tracking['item_id']
    ideal_price = tracking['ideal_price']
    refine_goal = tracking['refine_goal']
    enchant_requirement = tracking['enchant_requirement']

    result = check_nova_market(item_id = item_interested,
                      refine_goal = refine_goal,
                      ideal_price = ideal_price,
                      enchant_requirement = enchant_requirement
                      )

    print(result)
    
    if (len(result) > 0):

        print()

    return None


def get_tracking_items():

    MY_GAME_NAME = 'Babyish Storm'
    fire = firebase.FirebaseApplication(FIREBASE_URL, None)
    result = fire.get('/'+ MY_GAME_NAME, None)
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
