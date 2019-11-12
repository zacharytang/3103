from BaseScraper import BaseScraper
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from currency_converter import CurrencyConverter

class BukalapakScraper(BaseScraper):
    def __init__(self, keyword, write_queue):
        super().__init__(keyword, write_queue)
        
        # Override with search URL for site
        self.website = "Bukalapak"
        self.search_url = "https://www.bukalapak.com/products?search%5Bkeywords%5D={}".format(keyword)

    # Override with site-specific parsing
    def is_listing(self, url):
        parsed = urlparse(url)
        if parsed.path.startswith("/p/"):
            return True
        return False

    # Override with site-specific parsing
    def parse_listing(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find("h1", {"class": "c-product-detail__name"}).text.strip()
        price = soup.find_all(attrs={"data-reduced-price": True})[0]["data-reduced-price"]

        c = CurrencyConverter()
        price = c.convert(price, 'IDR', 'SGD')

        self.to_write.put((item, price, self.website))