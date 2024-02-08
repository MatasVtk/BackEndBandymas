#kazkas
#comentar

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from utils.models import CarAdverts
from utils.database import SessionLocal
from utils.paths import xPath
import time
import requests
import os
from urllib.parse import urlparse

class SCRAPER:
    def __init__(self, url):
        self.url = url
        self.manager = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.manager)
        self.driver.get(self.url)
        self.db = SessionLocal()
        self.a = 0
        self.max_iterations = 200
        self.iteration = 0
        self.photo_counter = 1


    def measure_time(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Run time:{execution_time:.1f} seconds")
            return result
        return wrapper

    def click_cookie(self):
        self.driver.implicitly_wait(2)
        try:
            self.driver.find_element('xpath', xPath.COOKIE_BUTTON).click()
        except:
            pass

    def compare_and_retrieve_urls(self):
        self.list_urls = []
        if self.a == 0:
            self.click_cookie()
            self.a+=1
        else:
            pass
        
        advert_ids_in_database = {str(advert_id[0]) for advert_id in self.db.query(CarAdverts.advert_id).all()}
        pages = self.driver.find_elements('xpath', xPath.LIST_ITEMS)
        for page in pages:
            advert_id = page.get_attribute('data-id')
            if advert_id not in advert_ids_in_database:
                self.list_urls.append(page.get_attribute('href') + '#gallery')
        return self.list_urls

    def retrieve_car_info(self):
        marke, modelis = self.driver.find_element('xpath', "//h1").text.split(' ', 1)
        set_of_car_info = {
            'make': marke,
            'model': modelis,
            'phone_number': self.find_element_wo_split(xPath.CONTACT_PHONE),
            'contact_name': self.find_element_wo_split(xPath.CONTACT_NAME),
            'city': self.find_element_wo_split(xPath.CONTACT_LOCATION),
            'price': ''.join(filter(str.isdigit, self.find_element_wo_split(xPath.MAIN_PRICE))),
            'year': self.find_element_w_split(xPath.MAKE_DATE)[:4] if len(self.find_element_w_split(xPath.MAKE_DATE)) > 4 else self.find_element_w_split(xPath.MAKE_DATE),
            'first_registration': self.find_element_w_split(xPath.ORIGIN_COUNTRY_ID),
            'engine_type': self.find_element_w_split(xPath.ENGINE),
            'body_type': self.find_element_w_split(xPath.BODY_TYPE_ID),
            'wheels_size': self.find_element_w_split(xPath.WHEEL_DRIVE_ID),
            'climate_control': self.find_element_w_split(xPath.CONDITION_TYPE_ID),
            'defects': self.find_element_w_split(xPath.HAS_DAMAGED_ID),
            'mileage': ''.join(filter(str.isdigit, self.find_element_w_split(xPath.KILOMETRAGE))) if self.find_element_w_split(xPath.KILOMETRAGE) != "none" else 0,
            'fuel_type': self.find_element_w_split(xPath.FUEL_ID),
            'gearbox': self.find_element_w_split(xPath.GEARBOX_ID),
            'color': self.find_element_w_split(xPath.COLOR_ID),
            'advert_id': self.find_element_w_split(xPath.ID)[1:],
            'url': self.driver.current_url
        }

        try:
            self.db.add(CarAdverts(**set_of_car_info))
            self.db.commit()
            self.download_photos()
        finally:
            self.db.close()
        return set_of_car_info

    def find_element_wo_split(self, xpathas, default_value = "none"):
        try:
            return self.driver.find_element('xpath', xpathas).text
        except:
            return default_value
        
    def find_element_w_split(self, xpathas, default_value = "none"):
        try:
            return self.driver.find_element('xpath', xpathas).text.split(': ', 1)[1]
        except:
            return default_value

    def find_photos(self):
        piclist = []
        image_urls = [element.get_attribute("src") or element.get_attribute("data-src") for element in self.driver.find_elements('xpath', xPath.PHOTO_LIST)]
        for url in image_urls:
            piclist.append(url)
        return piclist


    def next_page_button(self):
        try:
            url = self.driver.find_element('xpath', xPath.NEXT_PAGE_BUTTON).get_attribute('href')
        except NoSuchElementException:
            url = None
        return url

    @measure_time
    def run(self):
        while True:
            self.compare_and_retrieve_urls()
            for link in self.list_urls:
                self.driver.execute_script("window.open('about:blank', 'newtab')")
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(link)
                self.retrieve_car_info()
                self.driver.switch_to.window(self.driver.window_handles[0])
            next_page_url = self.next_page_button()
            if not next_page_url:
                break
            self.driver.get(next_page_url)
            self.iteration += 1
            if self.iteration >= self.max_iterations:
                break
        print('Done!')

    def download_photos(self):
        url_parts = urlparse(self.driver.current_url)
        advert_id = os.path.basename(url_parts.path).split('-')[-1].split('.')[0]
        folder_name = 'static/Skelbimu_Images/' +  advert_id
        os.makedirs(folder_name, exist_ok=True)
        for link in self.find_photos():
            try:
                r = requests.get(link)
                filename = os.path.join(folder_name, f"{self.photo_counter}.jpg")
                with open(filename, 'wb') as f:
                    f.write(r.content)
                self.photo_counter += 1  
            except requests.exceptions.RequestException as e:
                continue


url = input('Iveskite URL: ')
scraper = SCRAPER(url)
scraper.run()