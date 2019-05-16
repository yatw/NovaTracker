
# NovaTracker

A discord bot to help user track items on sell in the market, no more physically logging in and manually check it yourself!


## Personalize tracking preference

* User can set refine requirement and ideal price for each item he want to track.

* Tracker will only track that item with refine >= refine requirement is on sell <= ideal price

* Each user is allow to track up to five items

* Tracker will check the market every 15 minutes

* If any item match user's preference, NovaTracker will discord message the user

* If there are multiple items at the same refine level, NovaTracker will only show the cheaper item

* Sample notification 
When user requested to track Crimson Bow [2] refine >= 15 at price <= 800,000,000z


> Crimson Bow [2] +16 is on sell 450,000,000z at nova_vend,162,182


> Crimson Bow [2] +18 is on sell 639,999,999z at nova_vend,190,248



## Bot commands

* `!register`
	*Initialize user in the database, this registration is bond to the user's discord id*

* `!track item_id refine ideal_price`
	*Example: User want to track Lindy Hop [2] (21018) at refine >= 8, at price <= 200,000,000z*
	
	`!track 21018 8 200m`
	
	*ideal_price token accept k = 000, m = 000,000, and b = 000,000,000*

* `!untrack item_id`
	*Stop tracking the item*
	
* `!showtrack`
	*List all the item user is currently tracking*
	
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