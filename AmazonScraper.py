from BaseScraper import BaseScraper
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
import sys

class AmazonScraper(BaseScraper):
    def __init__(self, keyword, write_queue):
        super().__init__(keyword, write_queue)
        
        # Override with search URL for site
        self.website = "Amazon"
        self.search_url = "https://www.amazon.com/s?k={}".format(keyword)

    # Override with site-specific parsing
    def is_listing(self, url):
        parsed = urlparse(url)
        return True

    # Override with site-specific parsing
    def parse_listing(self, html):
        soup = BeautifulSoup(html, 'lxml') 
        item = soup.find("span", id="productTitle")
        price = soup.find(id="priceblock_ourprice")
        if price is None and item is None:
            return
        item = item.text.strip()
        price = '%.2f' % float(price.text.replace('$', ''))

        print("Item: {}, Price: ${}, From: {}".format(item, price, self.website))
        self.to_write.put((item, price, self.website))