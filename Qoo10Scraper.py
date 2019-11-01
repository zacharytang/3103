from BaseScraper import BaseScraper
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class Qoo10Scraper(BaseScraper):
    def __init__(self, keyword, write_queue):
        super().__init__(keyword, write_queue)
        
        # Override with search URL for site
        self.website = "Qoo10"
        self.search_url = "https://www.qoo10.sg/s/?keyword={}".format(keyword)

    # Override with site-specific parsing
    def is_listing(self, url):
        parsed = urlparse(url)
        if parsed.path.startswith("/item/"):
            return True
        return False

    # Override with site-specific parsing
    def parse_listing(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find("h2", {"id": "goods_name"}).text.strip()
        price = soup.find_all(attrs={"data-price": True})[0]["data-price"]

        print("Item: {}, Price: ${}, From: {}".format(item, price, self.website))
        self.to_write.put((item, price, self.website))