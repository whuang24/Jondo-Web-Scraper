from bs4 import BeautifulSoup
from csv import writer
from pprint import pprint
import time
import os.path
from selenium.webdriver.common.by import By
import unicodedata

from selenium import webdriver

#Change according to user account
username = 'VincentK'
password = 'Nwinc17667!'

#Copy and Paste the roll ID here with '' around them, separate by comma.
roll_id = ['900564','900592','900767','900921','900982','901055','901178','901210']

#Change according to the name required
file_name = 'orders.csv'

#URL of jondo website that is being accessed
url = 'https://jondohd.com/zencp/rollDetailsView?id='

#Change the number according to the time needed to solve reCaptcha
def sleeping():
    time.sleep(30)



#Access the geckodrier folder in local device
PATH = "D:\Programming\WebScraper\Scraper 3.3\geckodriver.exe"

driver = webdriver.Firefox(executable_path=PATH)
driver.get('https://jondohd.com/auth/0')

#Begins logging into website
driver.find_element(By.NAME, 'userName').send_keys(username)
driver.find_element(By.NAME, 'password').send_keys(password)
sleeping()


#Begins the scraping process
#MODIFIES: [accesses URL]/[creates fields for spreadsheet]/[collects data from specified rolls]
def scrape(url_link):
    driver.get(url_link)
    response = driver.page_source
    soup = BeautifulSoup(response, 'html.parser')
    table = soup.find_all('table')[1]
    items = table.find_all('tr')

    targets = list()
    targeted_items = set()
    orderIDs = set()

    # MODIFIES: ['targets' list]/ ['targeted_items' set]
    # EFFECT: adds every item within set [items] into set [targets] to prevent duplicates
    for item in items[1:]:
        targeted_items.add(item.find_all('td')[1].get_text())
        link = item.find('a').get_text()
        if link not in targets:
            targets.append(link)

    # MODIFIES: accessed individual items to retrieve data from them accordingly
    def find_info():
        for link in targets:
            OrderId = link
            driver.get("https://jondohd.com/workorder/" + link)
            sub = BeautifulSoup(driver.page_source, "html.parser")

            subtable = sub.find('table', {'class':'nested_item_table'})
            
            pictures = subtable.find_all('tr')[1:]
            
            for image in pictures:
                # Contents from the General Info Panel (Placed_by, PO, Shipping Date, Delivery Date)
                general = sub.find('table', {'class': 'form_table'})
                title = general.find('table', {'class':'form_table'})
                placed_by = title.find('td').get_text().strip(':')
                PONum = general.find('a').get_text()
                ordered_date = general.find_all('td')[5].get_text()
                shipped_date = general.find_all('td')[6].get_text()

                # Contents from the Item Details Tab (ImageID, width, height, ItemCode/Sku, Tracking Number, canvas, assembly, attribute)
                ImageInfo = image.find('td')
                ImageID = ImageInfo.find('a').get_text().strip()
                size = image.find_all('td')[3].get_text().split(' x ')
                width = size[0]
                height = size[1]
                SKU = image.find_all('td')[5].get_text()
                if 'Track number:' in SKU:
                    item_code = SKU.split('Track number:')[0].split('Item Number:')[0]
                    tracking = SKU.split('Track number:')[1]
                else:
                    item_code = SKU.split('Item Number:')[0]
                    tracking = ''
                canvas = image.find_all('td')[8].get_text().strip('Cut')
                assembly = image.find_all('td')[9].get_text()
                attr = image.find_all('td')[10]
                attribute = attr.find_all('div')[1].get_text()

                # Contents from the Order Details Tab (Customer)
                info = sub.find('table', {'class': 'orderDetail'})
                customer = info.find('td').get_text().strip(':')

                # Contents from the Order Details Tab (sub_total, shipping_price, shipping_cost, net_shipping)
                details = sub.find('table', {'class': 'pricingDetail'})
                sub_total = details.find_all('td')[0].get_text().strip(': USD ')
                shipping_price = details.find_all('td')[1].get_text().strip(': USD ')
                shipping_cost = details.find_all('td')[2].get_text().strip(': USD ')
                net_shipping = details.find_all('td')[3].get_text().strip(': USD ')

                # Contents from the Assets Tab (Title)
                assets = sub.find('table', {'class': 'assets_table'})
                thumb = assets.find_all('tr')[pictures.index(image) + 1]
                Title = thumb.find_all('td')[2].get_text()

                new_IC = item_code.replace('\n', '').replace('\xa0', '').replace(' ', '')

                strings = [ImageID, PONum, ordered_date, shipped_date, Title, OrderId, placed_by, width, height, new_IC, tracking, canvas, assembly, attribute, customer, sub_total, shipping_price, shipping_cost, net_shipping]

                print(strings)

                if ImageID in targeted_items:
                    if OrderId in orderIDs:
                        csv_writer.writerow([None, ImageID, PONum, ordered_date, shipped_date, Title, OrderId, width, height, new_IC, tracking, canvas, assembly, attribute, placed_by, customer, None, None, None, None])
                    else:
                        csv_writer.writerow([None, ImageID, PONum, ordered_date, shipped_date, Title, OrderId, width, height, new_IC, tracking, canvas, assembly, attribute, placed_by, customer, sub_total, shipping_price, shipping_cost, net_shipping])
                        orderIDs.add(OrderId)

    # MODIFIES: New CSV file
    # EFFECT: Initializes a CSV file and adds every item within visited to the file as the indicated organization

    if os.path.isfile('./' + file_name):
        with open(file_name, 'a', newline = '') as csv_file:
            csv_writer = writer(csv_file)
            Roll_ID = soup.find('h3').get_text()

            csv_writer.writerow([Roll_ID])
            find_info()
    else:
        with open(file_name, 'w', newline = '') as csv_file:
            csv_writer = writer(csv_file)
            headers = ['Roll ID', 'ImageID', 'PO#', 'Ordered Date', 'Shipped Date', 'Title', 'Order ID', 'Width', 'Height', 'Item Code/SKU', 'Track Number', 'Borders', 'Assembly', 'Attribute', 'Placed By', 'Customer', 'Cost', 'Shipping Price', 'Shipping Cost', 'Net Shipping Cost']
            csv_writer.writerow(headers)

            Roll_ID = soup.find('h3').get_text()

            csv_writer.writerow([Roll_ID])
            find_info()

for roll in roll_id:
    scrape(url + roll)