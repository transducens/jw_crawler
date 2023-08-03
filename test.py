import argparse
import logging
import os
import sys
from typing import List
from time import sleep
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

from src.SiteMap import SiteMap

log_format = (
    '[%(asctime)s] %(levelname)-8s %(message)s')

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    # filename="log.debug"
    stream=sys.stdout
)


def main():
    # user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0'
    options = Options()
    options.set_preference('intl.accept_languages', 'en-GB')
    # options.add_argument(f"user-agent={user_agent}")
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)
    site_map = SiteMap(url="https://www.jw.org/es/sitemap.xml", exclude=['lo-nuevo', 'politica-de-privacidad'])
    site_map.get_parallel_documents(driver=driver)
    exit(0)


main()
