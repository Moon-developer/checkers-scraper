# Scrape checkers website
import sqlite3

from requests import get
from lxml import html
from json import load


class CheckersProductScraper:
    def __init__(self):
        self.conn = sqlite3.connect('food_scraper.db')

        self.page_start = 0
        self.params = {'page': self.page_start,
                       'q': ':relevance:browseAllStoresFacetOff:browseAllStoresFacetOff'}
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "sec-ch-ua": "\"Google Chrome\";v=\"87\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"87\"",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
        }

    def setup_db(self):
        self.conn.execute(
            '''CREATE TABLE CHECKERS
                 (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                 TITLE  TEXT    NOT NULL,
                 PRICE  FLOAT   NOT NULL,
                 PRIMARY_CATEGORY  CHAR(256) NULL,
                 SECONDARY_CATEGORY  CHAR(256) NULL,
                 TERTIARY_CATEGORY  CHAR(256) NULL,
                 QUATERNARY_CATEGORY  CHAR(256) NULL,
                 IMAGE  CHAR(256));'''
        )

    def insert(self, title, price, image_src):
        self.conn.execute("INSERT INTO CHECKERS (TITLE,PRICE,IMAGE) VALUES (?, ?, ?)", (title, price, image_src))
        self.conn.commit()

    @staticmethod
    def get_links():
        with open('links/links.json', 'r') as f:
            links = load(f)
        return links

    def loop_links(self) -> None:
        links = self.get_links()
        for primary in links:
            for secondary in links[primary]:
                if isinstance(links[primary][secondary], str):
                    kwargs = {
                        'link': links[primary][secondary],
                        'primary': primary,
                        'secondary': secondary,
                    }
                    self.loop_pages(**kwargs)
                else:
                    for tertiary in links[primary][secondary]:
                        if isinstance(links[primary][secondary][tertiary], str):
                            kwargs = {
                                'link': links[primary][secondary][tertiary],
                                'primary': primary,
                                'secondary': secondary,
                                'tertiary': tertiary,
                            }
                            self.loop_pages(**kwargs)
                        else:
                            for quaternary in links[primary][secondary][tertiary]:
                                kwargs = {
                                    'link': links[primary][secondary][tertiary][quaternary],
                                    'primary': primary,
                                    'secondary': secondary,
                                    'tertiary': tertiary,
                                    'quaternary': quaternary,
                                }
                                self.loop_pages(**kwargs)

    def loop_pages(self, link: str, **kwargs):
        collective_products = []
        start_page = 0
        while retrieved := self.retrieve_all(link=link, page=start_page):
            collective_products.extend(retrieved)
            start_page += 1
        if collective_products:
            self.insert_products(items=collective_products, **kwargs)

    def insert_products(self, items, primary: str, secondary: str = None, tertiary: str = None,
                        quaternary: str = None):
        for item in items:
            values = (
                item['title'], item['price'], primary, secondary, tertiary, quaternary, item['image_src']
            )
            self.conn.execute(
                "INSERT INTO CHECKERS "
                "(TITLE,PRICE,PRIMARY_CATEGORY, SECONDARY_CATEGORY, TERTIARY_CATEGORY, QUATERNARY_CATEGORY, IMAGE) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                values)
            self.conn.commit()

    def retrieve_all(self, link: str, page: int = 0):
        self.params['page'] = page
        print(f'Link: {link}, page: {page}')
        response = get(f'https://www.checkers.co.za/{link}', params=self.params, headers=self.headers)
        items = []
        tree = html.fromstring(response.content)
        titles = tree.xpath('//a[@class="product-listening-click"]/text()')
        titles = [title.strip() for title in titles if title != ' ']
        if titles:
            prices = tree.xpath('//span[@class="now"]/text()')
            prices = [price for price in prices if price != ' ']
            cents = tree.xpath('//sup/text()')
            images = tree.xpath('//a[@class="product-listening-click"]/img/@data-original-src')
            images = ['https://www.checkers.co.za/' + image for image in images]
            items.extend([
                {'title': title, 'price': price + cent, 'image_src': image}
                for title, price, cent, image in zip(titles, prices, cents, images)
            ])
        return items


if __name__ == '__main__':
    checkers = CheckersProductScraper()

    # Setup database for first time if doesn't exist
    # checkers.setup_db()

    # Loop thru all navigation links and get items into database
    checkers.loop_links()
