import os
import logging
import time
import unicodedata
import graphyte
import re
import locale
import time

from selenium import webdriver
from bs4 import BeautifulSoup

logging.getLogger().setLevel(logging.INFO)
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
day_duration = 24 * 60 * 60

BASE_URL = 'https://coinpredictor.io/bitcoin#price'


def parse_page(page):
    paragraph_blocks = page.findAll('p')

    predictions = []
    for block in paragraph_blocks:
        match_obj = re.match(r'.* algorithm is estimating that within 24 hours BTC price will be ' +
                             r'<strong>.*</strong> ' +
                             r'targeting \$(.+), in 7 days .*', str(block))
        if match_obj:
            logging.info('Parsed %s ..', match_obj.group())
            predictions.append(('BTC', locale.atof(match_obj.group(1))))

    return predictions


GRAPHITE_HOST = 'graphite'


def send_metrics(predictions):
    sender = graphyte.Sender(GRAPHITE_HOST, prefix='currencies_predictions')
    for prediction in predictions:
        sender.send(prediction[0], prediction[1], timestamp=time.time() + day_duration)


def main():
    driver = webdriver.Remote(
        command_executor='http://selenium:4444/wd/hub',
        desired_capabilities={'browserName': 'chrome', 'javascriptEnabled': True}
    )

    driver.get(BASE_URL)
    time.sleep(5)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    metric = parse_page(soup)
    send_metrics(metric)

    driver.quit()

    logging.info('Accessed %s ..', BASE_URL)


if __name__ == '__main__':
    main()