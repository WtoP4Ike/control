import requests
from bs4 import BeautifulSoup
from random import randint
import sqlite3
import re


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.c = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.c.execute('''CREATE TABLE IF NOT EXISTS Restaurants 
                         (id integer PRIMARY KEY, 
                         restaurant_name TEXT, 
                         tags TEXT, 
                         average_bill TEXT, 
                         working_hours TEXT, 
                         address TEXT, 
                         phone TEXT, 
                         rating INTEGER)
                         ''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS RATINGS 
                         (id integer, 
                         text TEXT, 
                         rating TEXT)
                         ''')

    def insert_data(self, restaurant_data):
        self.c.execute(
            "INSERT INTO Restaurants (id, restaurant_name, tags, average_bill, working_hours, address, phone, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            restaurant_data)

    def insert_rating(self, restaurant_data):
        self.c.execute("INSERT INTO RATINGS (id, text, rating) VALUES (?, ?, ?)", restaurant_data)

    def commit(self):
        self.conn.commit()
    # def closebd(self):
    #    self.conn.close()


class Parser:

    def __init__(self, url):
        self.url = url

    def parse_reviews(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        restaurants = soup.find_all('div', class_='place-about')
        return restaurants


def sparse(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    restaurants = soup.find_all('div', class_='review-wrap')
    return restaurants


def main():
    print("Запускаюсь")  # дебаг меседж
    db = Database('wtop4ike.db')
    parser = Parser('https://www.restoran.ru/msk/catalog/restaurants/kitchen/european/')
    restaurants = parser.parse_reviews()
    idd = 0
    print("Код запущен и начинает работу")  # дебаг меседж
    for restaurant in restaurants:
        idd += 1
        name = restaurant.find('a', class_='name').text
        tags = restaurant.find('div', class_='props-wrap').text.replace("Кухня:  ", "").split("Время")[0].replace(
            "\xa0", " ")
        average_bill = restaurant.find('span', class_='average-bill').text
        working_hours = restaurant.find('div', class_='work-time').text.replace("Время работы: ", "")
        address = restaurant.find('div', class_='value').text
        phone = restaurant.find('div', class_='booking').text
        rating = restaurant.find('div', class_="rating-round-bg").text
        restaurant_data = (idd, name, tags, average_bill, working_hours, address, phone, rating)
        try:
            db.insert_data(restaurant_data)
        except:
            exit(
                "Ошибка при работе с базой данных: она уже была создана ранее, для создания новой удалите текущую или измените название файла")
        try:
            link = str(restaurant.find('div', class_="reviews-link")).split("window.open")[1].split(",")[0].replace(
                "('", "").replace("'", "")
            link = f"https://www.restoran.ru{link}"

        except Exception as e:
            pass
        otz = sparse(link)
        for one in otz:
            try:
                text = one.find('div', class_='review-text-wrap').find('span', class_='review-text-full').text
            except:
                text = one.find('div', class_='review-text-wrap').find('span', class_='review-text-preview').text
            try:
                reting = one.find('div', class_='review-rating has-grade-values').text
            except:
                reting = one.find('div', class_='review-rating').text
            rating = (idd, text, reting)
            db.insert_rating(rating)

    db.commit()
    print("Парсеринг закончен.")  # дебаг меседж


if __name__ == '__main__':
    main()