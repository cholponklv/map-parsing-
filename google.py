

import csv
import time
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import itertools
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import random


class GoogleMapScraper:
    def __init__(self):
        self.output_file_name = "Beta2.csv"
        self.headless = False
        self.driver = None
        self.unique_check = []
        self.count = 0

    def config_driver(self):
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        prefs = {"intl.accept_languages": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"}
        options.add_experimental_option("prefs", prefs)
        s = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=s, options=options)
        self.driver = driver

    def save_data(self, data):
        header = ['Название', 'Адрес', 'Город',
                  'Номер телефона', "Вебсайт", 'Cсылка']
        is_file_empty = not os.path.isfile(self.output_file_name) or os.stat(
            self.output_file_name).st_size == 0

        with open(self.output_file_name, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if is_file_empty:
                writer.writerow(header)
            writer.writerow(data)

    def parse_contact(self, business):
        try:
            contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[
                3].text.split("·")[-1].strip()
        except:
            contact = ""

        if "+7" not in contact:
            try:
                contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[
                    4].text.split("·")[-1].strip()
            except:
                contact = ""

        return contact

    def parse_address_and_category(self, business):
        try:
            address_block = business.find_elements(By.CLASS_NAME, "W4Efsd")[
                2].text.split("·")
            if len(address_block) >= 2:
                address = address_block[1].strip()
                category = address_block[0].strip()
            elif len(address_block) == 1:
                address = ""
                category = address_block[0]
        except:
            address = ""
            category = ""

        return address, category

    def get_business_info(self):

        businesses = self.driver.find_elements(By.CLASS_NAME, 'CpccDe')
        for business in businesses:
            name = business.find_element(
                By.CLASS_NAME, 'fontHeadlineSmall ').text
            address, category = self.parse_address_and_category(business)
            unique_id = "".join([name, address])
            if unique_id not in self.unique_check:
                contact = self.parse_contact(business)
                city = "Санкт-Петербург"
                try:
                    url = business.find_element(
                        By.CLASS_NAME, "hfpxzc").get_attribute("href")
                except NoSuchElementException:
                    url = ""
                try:
                    WebDriverWait(self.driver, 20).until(
                        EC.element_to_be_clickable(business))
                    ActionChains(self.driver).move_to_element(
                        business).perform()
                    business.location_once_scrolled_into_view
                    business.click()
                    time.sleep(2)
                    try:
                        website = self.driver.find_element(
                            By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[5]/a').get_attribute("href")
                        print(website)
                    except Exception as e:
                        try:
                            website = self.driver.find_element(
                                By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[3]/div/div[1]/div/div/div[2]/div[9]/div[6]/a').get_attribute("href")
                            print(website)
                        except:
                            website = ''
                except Exception as e:
                    website = ''

                data = [name, address, city, contact, website, url]
                self.save_data(data)
                self.unique_check.append(unique_id)
            else:
                self.count +=1
                print("Всего копий:", self.count, name, address)
         

    def scroll_to_end(self, scrollable_div):
        flag = True
        i = 0
        while flag:
            print(f"Scrolling to page {i + 2}")

            self.driver.execute_script(
                'arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)

            delay = random.uniform(2, 4)
            time.sleep(delay)

            no_results_element = self.driver.find_elements(
                By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[243]/div/p/span/span')
            if no_results_element:
                print("No more results.")
                flag = False
                break
            i += 1

    def load_companies(self, url):

        print("Getting business info", url)
        self.driver.get(url)

        time.sleep(3)
        panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        scrollable_div = self.driver.find_element(By.XPATH, panel_xpath)
        self.scroll_to_end(scrollable_div)
        self.get_business_info()


latitude_range = [59.651476 ,60.225695]
longitude_range = [29.410784 ,30.808707]


step = 0.3


coordinates_combinations = list(itertools.product(
    [round(latitude_range[0] + i * step, 7)
     for i in range(int((latitude_range[1] - latitude_range[0]) / step) + 1)],
    [round(longitude_range[0] + i * step, 7)
     for i in range(int((longitude_range[1] - longitude_range[0]) / step) + 1)]
))

urls = [
    f"https://www.google.com/maps/search/мужские+костюмы/@{lat},{lng},13z" for lat, lng in coordinates_combinations]
for index, value in enumerate(urls):
    print(f"Index: {index+1}, Value: {value}")
business_scraper = GoogleMapScraper()
business_scraper.config_driver()

s = 1

for url in urls:
    print(s, ' ', url)
    business_scraper.load_companies(url)
    s += 1
