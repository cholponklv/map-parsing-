

import csv
import time
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException,MoveTargetOutOfBoundsException,ElementNotInteractableException
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
        self.output_file_name = "yandexmap2.csv"
        self.headless = False
        self.driver = None
        self.unique_check = []
        self.count = 0
        self.slider = None

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


    def get_business_info(self):
        businesses = self.driver.find_elements(By.CLASS_NAME, 'search-snippet-view')
        print(len(businesses))
        for business in businesses:
            try:
                name = business.find_element(
                    By.CLASS_NAME, 'search-business-snippet-view__title ').text
                address = business.find_element(
                    By.CLASS_NAME, 'search-business-snippet-view__address').text
                unique_id = "".join([name, address])
                print(name, address)

                if unique_id not in self.unique_check:
                    city = "Москва"
                    try:
                        url = business.find_element(
                            By.CLASS_NAME, "search-snippet-view__link-overlay").get_attribute("href")
                        print(url, 'url')
                    except:
                        url = ""
                        print('error in url')
                    try:
                        WebDriverWait(self.driver, 20).until(
                            EC.element_to_be_clickable(business))
                        ActionChains(self.driver).move_to_element(
                            business).perform()
                        business.location_once_scrolled_into_view
                        business.click()
                        delay = random.uniform(1, 3)
                        time.sleep(delay)
                        
                        try:
                            website = self.driver.find_element(
                                By.CLASS_NAME, 'business-urls-view__link').get_attribute("href")
                            print(website)
                        except:
                            website = ''
                            print("нету вебсайта")
                        try:
                            contact = self.driver.find_element(By.CLASS_NAME, 'card-phones-view__number').text
                            contact = contact.replace('\n', '').replace('Показать телефон', '')
                        except:
                            contact = ''
                            print('ошибка в номере')
                    except Exception as e:
                        website = ''
                        contact = ''
                        print('ошибка при клике', e)

                    data = [name, address, city, contact, website, url]
                    print(data)
                    self.save_data(data)
                    self.unique_check.append(unique_id)
                else:
                    self.count +=1
                    print("Всего копий:", self.count, name,address)
            except:
                time.sleep(30)
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                print("name error")
                break
                    
         

    def scroll_to_end(self):
        start_time = time.time()
        while True:
            try:
                self.slider = self.driver.find_element(By.CLASS_NAME, 'scroll__scrollbar-thumb')

                ActionChains(self.driver).click_and_hold(self.slider).perform()

                ActionChains(self.driver).move_by_offset(0, 130).release().perform()

                delay = random.uniform(1, 4)
                time.sleep(delay)
                elapsed_time = time.time() - start_time
                if elapsed_time > 15:
                    break
            except NoSuchElementException:
                time.sleep(30)
            except MoveTargetOutOfBoundsException:
                
                break
            except ElementNotInteractableException:
                break
            
        


    def load_companies(self, url):

        print("Getting business info", url)
        self.driver.get(url)

        delay = random.uniform(2, 4)
        time.sleep(delay)
        self.scroll_to_end()
        self.get_business_info()


latitude_range = [55.158434, 55.920326]
longitude_range = [36.781755, 38.195622]


step = 0.1


coordinates_combinations = list(itertools.product(
    [round(latitude_range[0] + i * step, 7)
     for i in range(int((latitude_range[1] - latitude_range[0]) / step) + 1)],
    [round(longitude_range[0] + i * step, 7)
     for i in range(int((longitude_range[1] - longitude_range[0]) / step) + 1)]
))

urls = ['https://yandex.ru/maps/?ll=37.681755,55.858434&z=17&text=мужские%20с%20костюмы','https://yandex.ru/maps/?ll=37.781755,55.858434&z=17&text=мужские%20с%20костюмы','https://yandex.ru/maps/?ll=37.881755,55.858434&z=17&text=мужские%20с%20костюмы','https://yandex.ru/maps/?ll=37.981755,55.858434&z=17&text=мужские%20с%20костюмы','https://yandex.ru/maps/?ll=38.081755,55.858434&z=17&text=мужские%20с%20костюмы','https://yandex.ru/maps/?ll=38.181755,55.858434&z=17&text=мужские%20с%20костюмы']
for index, value in enumerate(urls):
    print(f"Index: {index+1}, Value: {value}")
business_scraper = GoogleMapScraper()
business_scraper.config_driver()

s = 1

for url in urls:
    print(s, ' ', url)
    business_scraper.load_companies(url)
    s += 1
