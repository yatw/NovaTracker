# NovaTracker

A discord bot to help user track items on sell in game


## Personalize tracking preference

* User can set refine requirement and ideal price for each item he want to track.

* Tracker will only track that item with refine > refine requirement is on sell < ideal price

* Each user is allow to track up to five items

* Tracker will check the market every 15 minutes

* If any item match user's preference, NovaTracker will discord message the user


## Bot commands

* `!register`
	*Initialize user in the database, this registration is bond to the user's discord id"

* `!track item_id refine ideal_price`
	*Example: User want to track Lindy Hop [2] (21018) at refine >= 8, at price <= 200,000,000z*
	*!track 21018 8 200m*
	*ideal_price token accept k = 000, m = 000,000, and b = 000,000,000*

* `!untrack item_id`
	*Stop tracking the item*
	
* `!showtrack`
	*List all the item user is currently tracking*
