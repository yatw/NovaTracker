

# NovaTracker

A discord bot to help user track items on sell in the market, no more physically logging in and manually checking it yourself!


## Personalize tracking preference

* User can set refine requirement and ideal price for each item he want to track.

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

* `!register`
	*Initialize user in the database, this registration is bond to the user's discord id*

* `!track item_id/item_name`
	*Example: User want to track Lindy Hop [2] (21018)*
	
	`!track 21018`
	
	*ideal_price token accept k = 000, m = 000,000, and b = 000,000,000*

* `!untrack item_id/item_name`
	*Stop tracking the item*
	
* `!clear`
	*Untrack all items at once*
	
* `!showtrack`
	*List all the items user is currently tracking*

* `!lowest`
	*Display the lowest price of the tracking items currently on market*
	
* `!report`
	*Allow user to report bug*

* `!quote`
	*Show my favourite quote at the moment*
	
* `!start`
	*Give a brief description of this bot for first time user*
	
* `!about`
	*Display user number and bot status*

* `!help`
	*List all the commands for this bot*
	
* `!contact`
	*Show my discord name for contact*



## Example
![alt text](https://github.com/yatw/NovaTracker/blob/master/example.png)


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
