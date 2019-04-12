from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import re

NOVA_MARKET_URL = 'https://www.novaragnarok.com/?module=vending&action=item&id=' 

#
#https://medium.freecodecamp.org/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe

# bypass forbidden with firefox
# https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping



def get_nova_page(item_id):

    global NOVA_MARKET_URL
    
    nova_url = NOVA_MARKET_URL + item_id

    req = Request(nova_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')

    return soup


# For this given item, check nova market
# return a dict { refine: [lowest price on market, location]}
def current_market_info(item_id, refinable):

    
    soup = get_nova_page(item_id)

    table = soup.find('table', {'id': 'itemtable'})

    if table is None:
        return None

    item_list = table.find_all('tr')
    
    on_sell = {

        0: {'price': -1, 'location': ""},
        1: {'price': -1, 'location': ""},
        2: {'price': -1, 'location': ""},
        3: {'price': -1, 'location': ""},
        4: {'price': -1, 'location': ""},
        5: {'price': -1, 'location': ""},
        6: {'price': -1, 'location': ""},
        7: {'price': -1, 'location': ""},
        8: {'price': -1, 'location': ""},
        9: {'price': -1, 'location': ""},
        10: {'price': -1, 'location': ""},
        11: {'price': -1, 'location': ""},
        12: {'price': -1, 'location': ""},
        13: {'price': -1, 'location': ""},
        14: {'price': -1, 'location': ""},
        15: {'price': -1, 'location': ""},
        16: {'price': -1, 'location': ""},
        17: {'price': -1, 'location': ""},
        18: {'price': -1, 'location': ""},
        19: {'price': -1, 'location': ""},
        20: {'price': -1, 'location': ""}
    }

    if (refinable):

        # Price, Refine, Addition Properties, Location
        for item in item_list[1:]:

            item_info = item.find_all('td')
            
            price    = int(item_info[0].text.strip().replace("z","").replace(",",""))
            refine   = int(item_info[1].text.strip().replace("\t","").replace("+",""))
            #enchant  = item_info[2].text
            location = item_info[3].text.strip()

            # first on sell item found
            if (on_sell[refine]['price'] == -1):
                on_sell[refine]['price'] = price
                on_sell[refine]['location'] = location

            elif (price < on_sell[refine]['price']):
                on_sell[refine]['price'] = price
                on_sell[refine]['location'] = location
    else:


        # Price, Qty, Location
        for item in item_list[1:]:

            item_info = item.find_all('td')
            
            price    = int(item_info[0].text.strip().replace("z","").replace(",",""))
            #qty   = int(item_info[1].text.strip().replace("\t","").replace("+",""))
            location = item_info[2].text.strip()

            # first on sell item found
            if (on_sell[0]['price'] == -1):
                on_sell[0]['price'] = price
                on_sell[0]['location'] = location

            elif (price < on_sell[0]['price']):
                on_sell[0]['price'] = price
                on_sell[0]['location'] = location  
            
    return on_sell

refinable_class = {
    'Headgear',
    'Armor',
    'Shield',
    'Shoes',
    'Footgear',
    'Garment',
    'Dagger',
    'One-Handed Sword',
    'Two-Handed Sword',
    'One-Handed Spear',
    'Two-Handed Spear',
    'One-Handed Axe',
    'Two-Handed Axe',
    'Mace',
    'Staff',
    'Bow',
    'Knuckle',
    'Musical Instrument',
    'Whip',
    'Book',
    'Katar',
    'Revolver',
    'Rifle',
    'Gatling Gun',
    'Shotgun',
    'Grenade Launcher',
    'Fuuma Shuriken',
    'Two-Handed Staff'
}


def can_refine(item_id):

    
    soup = get_nova_page(item_id)

    item_description = soup.find('div', {'class': 'item-desc'}).text

    class_des = re.search(r'(?<=Class: )\w+',item_description)
    if (class_des is None):
        return False
    
    item_class = class_des.group(0)

    if (item_class == "Headgear"):
        if (re.search(r'(?<=Location: )\w+',item_description).group(0) == "Upper"):
            return True
        else:
            return False
    
    
    return item_class in refinable_class
 
def search_item_name(item_id):
    ''' If item exist return item name, not return Unknown'''

    soup = get_nova_page(item_id)

    item_name = soup.find('div', {'class': 'item-name'}).text

    return item_name
