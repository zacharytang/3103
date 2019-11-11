from BaseScraper import BaseScraper
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import json
import re
import sys

class LazadaScraper(BaseScraper):
    def __init__(self, keyword, write_queue):
        super().__init__(keyword, write_queue)
        
        # Override with search URL for site
        self.website = "Lazada"
        self.search_url = "https://lazada.sg/catalog/?q={}".format(keyword)

    def parse_search_page(self, response):
        if not (response and response.status_code == 200):
            #print("Invalid search URL")
            sys.exit(1)

        html = response.text
        if "Sorry, something wrong" in html:
            print("Unable to crawl Lazada at this time...")
            sys.exit()
        root_url = '{}://{}'.format(urlparse(self.search_url).scheme, urlparse(self.search_url).netloc)

        soup = BeautifulSoup(html, 'html.parser')
        pattern = re.compile(r"window\.pageData=(\{.*?\})$")
        script = soup.find("script", text=pattern)

        data = pattern.search(script.text).group(1)
        data = json.loads(data)
        links = data["mods"]["listItems"]

        for link in links:
            url = "https:" + link["productUrl"]
            if url not in self.scraped_pages:
                self.to_crawl.put(url)

    # Override with site-specific parsing
    def parse_listing(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        item = soup.find("title").text.split(" | ")[0]
        pattern = re.compile(r"(\{\"offers\".*?\})$")
        script = soup.find("script", text=pattern)

        data = pattern.search(script.text).group(1)
        data = json.loads(data)
        price = data["offers"]["price"]

        self.to_write.put((item, price, self.website))