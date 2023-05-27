from bs4 import BeautifulSoup
from csv import writer
from csv import reader
import time
import os.path
from selenium.webdriver.common.by import By

from selenium import webdriver

class Scraper:

    def __init__(self):
        self.roll_id = []      #[921706, 921705, 921733]  (ID of the rolls to be scraped)
        self.username = ''    #'VincentK'      (Login Username)
        self.password = ''    #'FujSta17667!' (Login Password)
        self.file_name = ''   #Output file name
        self.url = 'https://jondohd.com/zencp/rollDetailsView?id='
        self.time = 0
        self.path = ""

    def __sleeping__(self):
        time.sleep(self.time)  

    def __driver_setup__(self):
        self.driver = webdriver.Firefox(executable_path=self.path)
        self.driver.get('https://jondohd.com/auth/0')

        self.driver.find_element(By.NAME, 'userName').send_keys(self.username)
        self.driver.find_element(By.NAME, 'password').send_keys(self.password)
        self.__sleeping__()


    def __write_to_file__(self, soup):
        with open(self.file_name, "r") as file:
            csv_reader = reader(file)
            first_row = next(csv_reader)

            if len(first_row) == 0:
                with open(self.file_name, 'a', newline = '') as csv_file:
                    self.csv_writer = writer(csv_file)
                    Roll_ID = soup.find('h3').get_text()

                    self.csv_writer.writerow([Roll_ID])
                    self.__find_info__()
            else:
                with open(self.file_name, 'w', newline = '') as csv_file:
                    self.csv_writer = writer(csv_file)
                    headers = ['Roll ID', 'ImageID', 'PO#', 'Ordered Date', 'Shipped Date', 'Order ID', 'Width', 'Height', 'Item Code/SKU', 'Track Number', 'Borders', 'Assembly', 'Attribute', 'Placed By', 'Customer', 'Cost', 'Shipping Price', 'Shipping Cost', 'Net Shipping Cost']
                    self.csv_writer.writerow(headers)

                    Roll_ID = soup.find('h3').get_text()

                    self.csv_writer.writerow([Roll_ID])
                    self.__find_info__()
    

    def __find_info__(self):
        for link in self.targets:
            OrderId = link
            self.driver.get("https://jondohd.com/workorder/" + link)
            sub = BeautifulSoup(self.driver.page_source, "html.parser")

            subtable = sub.find('tbody', {'id':'itemDetailsBody'})

            pictures = subtable.find_all('tr')
            
            for image in pictures:
                # Contents from the General Info Panel (Placed_by, PO, Shipping Date, Delivery Date)
                general = sub.find_all('span', {'class' : 'orderDetailItemData'})
                placed_by = general[0].get_text().strip()
                PONum = general[3].get_text()
                ordered_date = general[12].get_text()
                shipped_date = general[15].get_text()

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
                assembly = image.find_all('td')[9].get_text().replace('\n', ' ').strip()
                attribute = image.find_all('td')[10].get_text()

                # Contents from the Order Details Tab (Customer)
                customer_details = sub.find_all('div', {'class' : 'orderDetailBox columnBody'})[2]
                customer = customer_details.find('span', {'class' : 'orderDetailItemData'}).get_text()

                # Contents from the Order Details Tab (sub_total, shipping_price, shipping_cost, net_shipping)
                pricing_details = sub.find('div', {'id': 'pricingBody'})
                pricing_numbers = pricing_details.find_all('div', {'class' : 'flexColumn'})[1]
                pricing = pricing_numbers.find_all('span')
                sub_total = pricing[0].get_text()
                shipping_price = pricing[1].get_text()
                shipping_cost = pricing[-2].get_text()
                net_shipping = pricing[-1].get_text()

                new_IC = item_code.replace('\n', '').replace('\xa0', '').replace(' ', '')

                strings = [ImageID, PONum, ordered_date, shipped_date, OrderId, placed_by, width, height, new_IC, tracking, canvas, assembly, attribute, customer, sub_total, shipping_price, shipping_cost, net_shipping]

                #Uncomment the following print line if wish to see feedback on console
                print(strings)

                if ImageID in self.targeted_items:
                    if OrderId in self.order_IDs:
                        self.csv_writer.writerow([None, ImageID, PONum, ordered_date, shipped_date, OrderId, width, height, new_IC, tracking, canvas, assembly, attribute, placed_by, customer, None, None, None, None])
                    else:
                        self.csv_writer.writerow([None, ImageID, PONum, ordered_date, shipped_date, OrderId, width, height, new_IC, tracking, canvas, assembly, attribute, placed_by, customer, sub_total, shipping_price, shipping_cost, net_shipping])
                        self.order_IDs.add(OrderId)

    

    def __scrape__(self, url_link):
        self.driver.get(url_link)
        response = self.driver.page_source
        soup = BeautifulSoup(response, 'html.parser')
        table = soup.find_all('table')[1]
        items = table.find_all('tr')

        self.targets = list()
        self.targeted_items = set()
        self.order_IDs = set()

        # MODIFIES: ['targets' list]/ ['targeted_items' set]
        # EFFECT: adds every item within set [items] into set [targets] to prevent duplicates
        for item in items[1:]:
            self.targeted_items.add(item.find_all('td')[1].get_text())
            link = item.find('a').get_text()
            if link not in self.targets:
                self.targets.append(link)

        self.__write_to_file__(soup)

        # if os.path.isfile('./' + self.file_name):
        #     with open(self.file_name, 'a', newline = '') as csv_file:
        #         self.csv_writer = writer(csv_file)
        #         Roll_ID = soup.find('h3').get_text()

        #         self.csv_writer.writerow([Roll_ID])
        #         self.__find_info__()
        # else:
        #     with open(self.file_name, 'w', newline = '') as csv_file:
        #         self.csv_writer = writer(csv_file)
        #         headers = ['Roll ID', 'ImageID', 'PO#', 'Ordered Date', 'Shipped Date', 'Order ID', 'Width', 'Height', 'Item Code/SKU', 'Track Number', 'Borders', 'Assembly', 'Attribute', 'Placed By', 'Customer', 'Cost', 'Shipping Price', 'Shipping Cost', 'Net Shipping Cost']
        #         self.csv_writer.writerow(headers)

        #         Roll_ID = soup.find('h3').get_text()

        #         self.csv_writer.writerow([Roll_ID])
        #         self.__find_info__()

    def start(self):
        self.__driver_setup__()

        for roll in self.roll_id:
            self.__scrape__(self.url + roll)


