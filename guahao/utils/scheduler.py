import time
import schedule

from .ext_register import CrawlGuaHao
from .combination import Combination
from .local_to_remote import Transfer
from guahao.start import run

crawl = CrawlGuaHao()
combine = Combination()
transfer = Transfer()

schedule.every().day.at("7:00").do(crawl.main)
schedule.every().day.at("8:10").do(combine.save_to_mongo)
schedule.every().day.at("8:30").do(transfer.transfer_data)
schedule.every().sunday.at("8:00").do(run)

while True:
    schedule.run_pending()
    time.sleep(60)
