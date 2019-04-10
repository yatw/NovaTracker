from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

NOVA_MARKET_URL = 'https://www.novaragnarok.com/?module=vending&action=item&id=' 


#
#https://medium.freecodecamp.org/how-to-scrape-websites-with-python-and-beautifulsoup-5946935d93fe

# bypass forbidden with firefox
# https://stackoverflow.com/questions/16627227/http-error-403-in-python-3-web-scraping

def check_nova_market(item_id, ideal_price, refine_goal):

    item_match = []

    global NOVA_MARKET_URL
    
    market_url = NOVA_MARKET_URL + str(item_id)

    req = Request(market_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')


    table = soup.find('table', {'id': 'itemtable'})
    item_list = table.find_all('tr')


    for item in item_list[1:]:

        item_info = item.find_all('td')
        
        price    = int(item_info[0].text.strip().replace("z","").replace(",",""))
        refine   = int(item_info[1].text.strip().replace("\t","").replace("+",""))
        enchant  = item_info[2].text
        location = item_info[3].text

        if (price <= ideal_price) and (refine >= refine_goal):
            item_match.append({'price': price, 'refine': refine, 'location': location})

    message = ""      

    return message

def search_item_name(item_id):
    ''' If item exist return item name, not return Unknown'''


    global NOVA_MARKET_URL

    market_url = NOVA_MARKET_URL + str(item_id)

    req = Request(market_url, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req).read()
    soup = BeautifulSoup(page, 'html.parser')

    item_name = soup.find('div', {'class': 'item-name'}).text

    return item_name




    
