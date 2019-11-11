import requests
import sys
from bs4 import BeautifulSoup
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse, urldefrag
from threading import Thread
from time import sleep

class BaseScraper(Thread):
    def __init__(self, keyword, write_queue):
        super().__init__()

        self.to_write = write_queue
        self.pool = ThreadPoolExecutor(max_workers=20)
        self.scraped_pages = set([])
        self.to_crawl = Queue()

        # change these to your website's search url
        self.website = "Example"
        self.search_url = "http://www.example.com"

    def parse_search_page(self, response):
        if not (response and response.status_code == 200):
            #print("Invalid search URL")
            sys.exit(1)

        html = response.text
        root_url = '{}://{}'.format(urlparse(self.search_url).scheme, urlparse(self.search_url).netloc)

        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all(href=True)

        for link in links:
            url = link['href']
            url, throwaway = urldefrag(url)
            if url.startswith('/'):
                url = urljoin(root_url, url)
            if not self.is_listing(url):
                continue
            if url not in self.scraped_pages:
                self.to_crawl.put(url)

    # Override this method to parse your website's listing urls only
    # Return True if is a valid listing url, False otherwise
    def is_listing(self, url):
        # Dummy value
        return True

    def post_scrape_callback(self, res):
        result = res.result()
        if result and result.status_code == 200:
            self.parse_listing(result.text)

    # Override this method to parse item name and price
    # Insert into write queue as a tuple: <name, price, site>
    def parse_listing(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all(href=True)

        # Dummy values
        item, price = ("Camera", "123.45")
        print("Item: {}, Price: ${}, From: {}".format(item, price, self.website))
        self.to_write.put((item, price, self.website))

    def scrape_page(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
            res = requests.get(url, headers=headers, timeout=10)
            return res
        except requests.RequestException:
            return
 
    def run(self):
        # scrape original website
        search_res = self.scrape_page(self.search_url)
        self.parse_search_page(search_res)

        # go through each listing url
        while True:
            try:
                target_url = self.to_crawl.get(timeout=10)
                if target_url not in self.scraped_pages:
                    self.scraped_pages.add(target_url)
                    job = self.pool.submit(self.scrape_page, target_url)
                    job.add_done_callback(self.post_scrape_callback)

                    # reduce request rate
                    sleep(2)
            except Empty:
                return
            except Exception as e:
                print(e)
                continue