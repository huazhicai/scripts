from scrapy import cmdline
import time


def run():
    for i in ['114yygh', '114gh']:
        time.sleep(3)
        cmdline.execute("scrapy crawl {}".format(i).split())


# cmdline.execute("scrapy crawl 114gh".split())
