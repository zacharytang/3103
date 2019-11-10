import os
import sys
import multiprocessing
from queue import Queue, Empty
from threading import Thread

from Qoo10Scraper import Qoo10Scraper
from CarousellScraper import CarousellScraper
from LazadaScraper import LazadaScraper
from AmazonScraper import AmazonScraper

def get_program_runtime():
    return 2*60

class WriterThread(multiprocessing.Process):
    def __init__(self, to_write):
        super().__init__()
        self.to_write = to_write

    def run(self):
        # TODO: write to CSV
        with open("scraper_output.csv", "w") as output_file:
            i = 1
            min_price = 999999999999
            while True:
                try:
                    if i == 1:
                        output_file.write("Item,Price (SGD$),Website")

                    item, price, website = self.to_write.get(timeout=10)
                    price = str(price).replace(",","")
                    if float(price) < min_price and float(price) > 1.0:
                        min_price = float(price)
                        cheapest_item = item
                        cheapest_site = website

                    print("Number of listings scraped: {}".format(i), end='\r')
                    sys.stdout.flush()

                    output_file.write("\n{},{},{}".format(item.replace(",", ""), price, website))
                    # flush output to file
                    # TODO: change to more reasonable strategy, flushing every line is expensive
                    if i % 10 == 1:
                        output_file.flush()
                        os.fsync(output_file.fileno())
                    i += 1
                except Empty:
                    print("Number of listings scraped: {}".format(i))
                    print("Cheapest item found on {}: {}, ${}".format(cheapest_site, cheapest_item, min_price))
                    print("Writing queue empty, exiting program. Output written to scraper_output.csv")
                    return
                except Exception as e:
                    print(e)
                    continue


def start_scraper(keyword):
    print("Starting search for: {}".format(keyword))
    print("Running scraper for {}s\n".format(get_program_runtime()))

    # initialize write queue, should be passed to each scraper
    to_write = multiprocessing.Queue()
    writer_thread = WriterThread(to_write)
    writer_thread.start()

    # initialize and start all scrapers
    scraper_list = []
    # e.g. 
    scraper_list.append(Qoo10Scraper(keyword, to_write))
    scraper_list.append(CarousellScraper(keyword, to_write))
    scraper_list.append(LazadaScraper(keyword, to_write))
    scraper_list.append(AmazonScraper(keyword, to_write))

    for scraper in scraper_list:
        scraper.start()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: project_main.py <keyword>")
        sys.exit(1)

    p = multiprocessing.Process(target=start_scraper, args=(sys.argv[1],), name="start")
    p.start()

    # set timeout
    p.join(get_program_runtime())

    if p.is_alive():
        # terminate "main" thread
        p.terminate()
        p.join()