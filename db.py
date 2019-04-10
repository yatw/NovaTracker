import asyncio
 
import re

from bot_config import DISCORD_TOKEN, db
from novamarket import check_nova_market, get_item_name


db.users.insert(
        {
            'DISCORD_ID' : 3366,
            'INTERESTED_ITEMS' : []
        }
)
