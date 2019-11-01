import os
import sys
import multiprocessing
from queue import Queue, Empty
from threading import Thread

from Qoo10Scraper import Qoo10Scraper
from CarousellScraper import CarousellScraper

def get_program_runtime():
    return 5*60

class WriterThread(multiprocessing.Process):
    def __init__(self, to_write):
        super().__init__()
        self.to_write = to_write

    def run(self):
        # TODO: write to CSV
        with open("scraper_output.csv", "w") as output_file:
            i = 1
            while True:
                try:
                    if i == 1:
                        output_file.write("Item,Price (SGD$),Website")

                    item, price, website = self.to_write.get(timeout=10)
                    output_file.write("\n{},{},{}".format(item, price, website))
                    # flush output to file
                    # TODO: change to more reasonable strategy, flushing every line is expensive
                    output_file.flush()
                    os.fsync(output_file.fileno())
                    i += 1
                except Empty:
                    print("Writing queue empty, exiting")
                    return
                except Exception as e:
                    print(e)
                    continue


def start_scraper(keyword):
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