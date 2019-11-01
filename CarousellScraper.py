from BaseScraper import BaseScraper
from urllib.parse import urlparse
from bs4 import BeautifulSoup

class CarousellScraper(BaseScraper):
    def __init__(self, keyword, write_queue):
        super().__init__(keyword, write_queue)
        
        # Override with search URL for site
        self.website = "Carousell"
        self.search_url = "https://sg.carousell.com/search/products/?query={}".format(keyword)

    # Override with site-specific parsing
    def is_listing(self, url):
        parsed = urlparse(url)
        if parsed.path.startswith("/p/"):
            return True
        return False

    # Override with site-specific parsing
    def parse_listing(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find("meta", property="og:title")
        item_name = (item["content"])
        price = soup.find("meta", attrs={"name": "twitter:data1"})
        actual_price = (price.attrs.get('content'))[2:]

        print("Item: {}, Price: ${}, From: {}".format(item_name, actual_price, self.website))
        self.to_write.put((item_name, actual_price, self.website))