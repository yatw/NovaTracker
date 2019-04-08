import os
import pymongo
#from dotenv import load_dotenv

MY_PHONE_NUMBER = os.environ.get("MY_PHONE_NUMBER")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TEST_TWILIO_ACCOUNT_SID = os.environ.get("TEST_TWILIO_ACCOUNT_SID")
TEST_TWILIO_AUTH_TOKEN = os.environ.get("TEST_TWILIO_AUTH_TOKEN")
FIREBASE_URL = os.environ.get("FIREBASE_URL")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")



MONGO_URL = os.environ.get('MONGOATLAS_URI')
client = pymongo.MongoClient(MONGO_URL, 27017)
db = client.test

