

import csv
import time
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import os
import itertools

class GoogleMapScraper:
    def __init__(self):
        self.output_file_name = "google_map_business_data6.csv"
        self.headless = False
        self.driver = None
        self.unique_check = []
        

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
        header = ['Название', 'Адрес', 'Категория', 'Номер телефона', 'ссылка']
        is_file_empty = not os.path.isfile(self.output_file_name) or os.stat(self.output_file_name).st_size == 0

        with open(self.output_file_name, 'a', newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            if is_file_empty:
                writer.writerow(header)
            writer.writerow(data)

    def parse_contact(self, business):
        try:
            contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[3].text.split("·")[-1].strip()
        except:
            contact = ""

        if "+7" not in contact:
            try:
                contact = business.find_elements(By.CLASS_NAME, "W4Efsd")[4].text.split("·")[-1].strip()
            except:
                contact = ""

        return contact



    def parse_address_and_category(self, business):
        try:
            address_block = business.find_elements(By.CLASS_NAME, "W4Efsd")[2].text.split("·")
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
        time.sleep(2)
        
        for business in self.driver.find_elements(By.CLASS_NAME, 'CpccDe'):
            name = business.find_element(By.CLASS_NAME, 'fontHeadlineSmall ').text
            address, category = self.parse_address_and_category(business)
            contact = self.parse_contact(business)
            try:
                website = business.find_element(By.CLASS_NAME, "hfpxzc").get_attribute("href")
            except NoSuchElementException:
                website = ""

            unique_id = "".join([name, address, category, contact, website])
            if unique_id not in self.unique_check:
                data = [name, address, category, contact, website]
                self.save_data(data)
                self.unique_check.append(unique_id)



    def load_companies(self, url):
        
        print("Getting business info", url)
        self.driver.get(url)
        time.sleep(5)
        panel_xpath = '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]'
        scrollable_div = self.driver.find_element(By.XPATH, panel_xpath)
        
        # scrolling
        flag = True
        i = 0
        try:
            checkbox_button = self.driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[3]/button')
            aria_checked = checkbox_button.get_attribute("aria-checked")
            if aria_checked == "true":
                print("Checkbox is already checked")
            else:
                # Нажимаем на кнопку "Обновлять результаты при смещении карты"
                checkbox_button.click()
                print("Checkbox clicked")
        except NoSuchElementException:
            print("Checkbox not found")
        while flag:
            print(f"Scrolling to page {i + 2}")
            self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(2)
            no_results_element = self.driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[1]/div[1]/div[243]/div/p/span/span')
            if no_results_element:
                print("No more results.")
                flag = False
                break
            if "You've reached the end of the list." in self.driver.page_source:
                flag = False

            self.get_business_info()
            i += 1


latitude_range = [55.138434, 55.920326]
longitude_range = [36.481755,38.195622]


# Шаг изменения координат
step = 0.2


coordinates_combinations = list(itertools.product(
    [round(latitude_range[0] + i * step, 7) for i in range(int((latitude_range[1] - latitude_range[0]) / step) + 1)],
    [round(longitude_range[0] + i * step, 7) for i in range(int((longitude_range[1] - longitude_range[0]) / step) + 1)]
))
# Генерируем URL-адреса
urls = [f"https://www.google.com/maps/search/мужские+костюмы/@{lat},{lng},13z" for lat, lng in coordinates_combinations]
for index, value in enumerate(urls):
    print(f"Index: {index}, Value: {value}")
business_scraper = GoogleMapScraper()
business_scraper.config_driver()

# Загружаем данные для каждого URL-адреса
for url in urls:
    print(url)
    business_scraper.load_companies(url)