import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List
import csv
import traceback
import datetime

@dataclass
class Car:
    link: str
    full_name: str
    description: str
    year: int
    mileage_km: str
    engine_capacity: str
    fuel_type: str
    horsepower: str
    price_pln: int



##### Configuration #####

# URL to scrape - example:
# from "https://www.otomoto.pl/osobowe/uzywane/dodge/charger/od-2015?page=5&search%5Badvanced_search_expanded%5D=true" get only "uzywane/dodge/charger/od-2015"
url_to_scrape = "uzywane/dodge/charger/od-2015"

# Number of pages to scrape
# get it from the website from bottom of the page
number_of_pages_to_scrape = 5

element_of_offer_table = "div"
class_of_offer_table = "ooa-r53y0q ezh3mkl11"

element_of_cars = "article"
class_of_cars = "ooa-yca59n emjt7sh0"

element_of_stats_block = "p"
class_of_stats_block = "emjt7sh10 ooa-1tku07r er34gjf0"

element_of_car_title = "h1"
class_of_car_title = "emjt7sh9 ooa-1ed90th er34gjf0"

element_of_all_data = "dd"

element_of_price = "h3"
class_of_price = "emjt7sh16 ooa-1n2paoq er34gjf0"

# add to the end of the file name current date and time

output_file_name = "cars_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"

#########################



class OtomotoScraper:
    def __init__(self, car_make: str) -> None:
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.11 (KHTML, like Gecko) "
            "Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }
        self.car_make = car_make

        self.website = "https://www.otomoto.pl/osobowe"

    def scrape_pages(self, number_of_pages: int) -> List[Car]:
        cars = []
        for i in range(1, number_of_pages + 1):
            current_website = f"{self.website}/{self.car_make}/?page={i}"
            new_cars = self.scrape_cars_from_current_page(current_website)
            if new_cars:
                cars += new_cars
        return cars

    def scrape_cars_from_current_page(self, current_website: str) -> List[Car]:
        try:
            response = requests.get(current_website, headers=self.headers).text
            soup = BeautifulSoup(response, "html.parser")
            cars = self.extract_cars_from_page(soup)
            return cars
        except Exception as e:
            print(f"Problem with scraping website: {current_website}, reason: {e}")
            return []

    def extract_cars_from_page(self, soup: BeautifulSoup) -> List[Car]:
        offers_table = soup.find(element_of_offer_table, class_=class_of_offer_table)
        cars = offers_table.find_all(element_of_cars, class_=class_of_cars)
        list_of_cars = []
        for car in cars:
            try:
                stats_block = car.find(element_of_stats_block, class_=class_of_stats_block).text.split("•")

                car_title = car.find(element_of_car_title, class_=class_of_car_title).a
                
                link = car_title.get("href")

                full_name = car_title.text

                if len(stats_block) == 3 :
                    description = stats_block[2].strip()
                else:
                    description = "No description"
            
                engine_capacity = stats_block[0].strip()

                horsepower = stats_block[1].strip()
               
                all_data = car.find_all(element_of_all_data)

                year = all_data[3].text.strip()
  
                mileage_km = all_data[0].text.strip()

                fuel_type = all_data[1].text.strip()

                price_pln = car.find(element_of_price, class_=class_of_price).text.replace(" ", "")

                list_of_cars.append(
                    Car(
                        link=link,
                        full_name=full_name,
                        description=description,
                        year=year,
                        mileage_km=mileage_km,
                        engine_capacity=engine_capacity,
                        fuel_type=fuel_type,
                        horsepower=horsepower,
                        price_pln=price_pln,
                    )
                )
            except:
                print(traceback.format_exc())
        return list_of_cars


def write_to_csv(cars: List[Car]) -> None:
    with open(output_file_name, mode="w") as f:
        fieldnames = [
            "link",
            "full_name",
            "description",
            "year",
            "mileage_km",
            "engine_capacity",
            "fuel_type",
            "horsepower",
            "price_pln",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for car in cars:
            writer.writerow(asdict(car))


def scrape_otomoto() -> None:
    scraper = OtomotoScraper(url_to_scrape)
    cars = scraper.scrape_pages(number_of_pages_to_scrape)
    write_to_csv(cars)


if __name__ == "__main__":
    scrape_otomoto()
