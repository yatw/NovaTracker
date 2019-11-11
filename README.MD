

# NovaTracker

A discord bot to help user track items on sell in the market, no more physically logging in and manually checking it yourself!

### [To add this bot to your server](https://discordapp.com/api/oauth2/authorize?client_id=571526126602813441&permissions=2048&scope=bot)

#### This project is outdated and no longer functional
  
## About the project


#### Ambition

There is always that one item that is either never on sell or always overprice. If you still really want it, you either have to constantly monitor the chat channel or actively check the market yourself.

#### How to use

This bot is freely available to all Nova Ragnarok players. Simply invite this bot to your server or join a server that already has this bot. This bot is meant to privately take in commands, as such, it will only response through private message. Once you have set up your preference, you will get on sell notification.


**This bot must need your permission to allow private dm, otherwise it cannot notify you and will delete you as a user!**   
**inside your discord setting-> privacy & safety-> Turn ON Allow direct message from server member**

#### Technologies

- **Language**: Python
- **Discord development**: [Discord rewrite Rapptz](https://github.com/Rapptz/discord.py)
- **Database**: [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- **Web scraping**: Beautiful Soup
- **Hosting**: AWS EC2 instance

#### Known Issue

1. Sometime user will not receive response because inside discord setting-> privacy & safety-> Allow direct message from server member is turned off.

2. Sometime the recurring market check will stop, and in that case I will have to restart the program on AWS.

#### Challenges
1. Nova website require login to access the market data
2. Market data are dynamically generated from JavaScript

## Personalize tracking preference

* User can set refine requirement and ideal price for each item he wants to track.

* Tracker will only track that item with refine >= refine requirement is on sell <= ideal price

* Each user is allow to track up to **10** items

* Tracker will check the market every **15** minutes

* If any item match user's preference, NovaTracker will discord message the user

* If there are multiple items at the same refine level, NovaTracker will only show the cheaper item

* Sample notification

When user requested to track Crimson Bow [2] refine >= 15 at price <= 800,000,000z

> Crimson Bow [2] +16 is on sell 450,000,000z at nova_vend,162,182

> Crimson Bow [2] +18 is on sell 639,999,999z at nova_vend,190,248

## Bot commands

*  `!register`
*Initialize user in the database, this registration is bond to the user's discord id*

*  `!track [item_id/item_name]`
*Example: User want to track Lindy Hop [2] (21018)*

*   `!track 21018` or `!track lindy`
*ideal_price token accept k = 000, m = 000,000, and b = 000,000,000*

*  `!untrack [item_id/item_name]`
*Stop tracking the item*

*  `!clear`
*Untrack all items at once*

*  `!showtrack`
*List all the items user is currently tracking*

*  `!lowest`
*Display the lowest price of the tracking items currently on market*

*  `!quote`
*Randomly show one of my favourite quote*

*  `!start`
*Give a brief description of this bot for first time user*

*  `!about`
*Display user number and bot status*

*  `!doc`
*Disply link to github documentation*
  
*  `!help`
*List all the commands for this bot*

*  `!contact`
*Feel free to reach out to me*

## Demo

![alt text](https://github.com/yatw/NovaTracker/blob/master/example.png)


## Contributing

If you would like to make this a better bot, I welcome to you contact me and I would love to hear your ideas.

Currently I am looking for a way to track market data in real time (rather than checking periodically), as well as an efficient way to compare the new market data and decide rather to notify the users.


## Hosting Instructions

### Dependencies

**Note that the following was done in Window OS**

```
python -m pip install --user -U https://github.com/Rapptz/discord.py/archive/rewrite.zip
pip install pytz
pip install pymongo
pip install dnspython
pip install BeautifulSoup4
```
### On Ubuntu

```
sudo apt install python3
sudo snap install discord
python3 -m pip install --user -U https://github.com/Rapptz/discord.py/archive/rewrite.zip
python3 -m pip install pytz
python3 -m pip install pymongo
python3 -m pip install dnspython
python3 -m pip install BeautifulSoup4
```
**For it to keep running, inside Ubuntu instance**

```
screen
leave screen (Ctrl A+D)
go back to screen(screen -r number)
```

**To delete a screen**
```
screen -X -S [session # you want to kill] quit
```

**To start running the bot on Ubuntu**
```
python3 NovaTracker.py
```
