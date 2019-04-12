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
# return a dict { refine: lowest price on market}
def current_market_info(item_id):

    item_match = []

    global NOVA_MARKET_URL

    soup = get_nova_page(item_id, NOVA_MARKET_URL)
    print(soup)

    table = soup.find('table', {'id': 'itemtable'})
    item_list = table.find_all('tr')


    for item in item_list[1:]:

        item_info = item.find_all('td')
        
        price    = int(item_info[0].text.strip().replace("z","").replace(",",""))
        refine   = int(item_info[1].text.strip().replace("\t","").replace("+",""))
        enchant  = item_info[2].text
        location = item_info[3].text


    message = ""      

    return message


#current_market_info('4128')



def search_item_name(item_id):
    ''' If item exist return item name, not return Unknown'''

    soup = get_nova_page(item_id)

    item_name = soup.find('div', {'class': 'item-name'}).text

    return item_name


refinable_class = {'Weapon', 'Armor'}


def can_refine(item_id):

    
    soup = get_nova_page(item_id)

    item_description = soup.find('div', {'class': 'item-desc'})
    print(item_description)


    result = re.findall(r'(Class:)$', "f")
    print(result)
    '''
    
    table = soup.find('table', {'id': 'itemtable'})
    print(table
    item_list = table.find_all('tr')

    item = item_list[0] # there should be only 1 item
    item_info = item.find_all('td')
    print(item_info[3].text.strip())
    # 0 item_id
    # 1 image
    # 2 item_name
    # 3 item_type
    '''
    return False
    

        
can_refine('15042')


