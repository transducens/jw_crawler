import logging
import sys
import json
import requests
import os
import argparse
import pandas as pd
from time import sleep
from typing import List, Dict
from lxml import etree
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from selenium.webdriver.firefox.options import Options
from selenium import webdriver

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

LANGS = [
    'es',
    'cak',
    'kek',
    'mam',
    'kjb',
    'ctu',
    'quc',
    'poh',
    'tzh',
    'tzo',
    'yua',
]

log_format = (
    '[%(asctime)s] %(levelname)-8s %(message)s')

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    stream=sys.stdout
)


def check_cookies_button(driver: webdriver):
    try:
        sleep(2)
        x_path_exp_cookies = ".//button[@class='lnc-button lnc-button--primary lnc-declineCookiesButton']"
        cookies_button = driver.find_element(By.XPATH, x_path_exp_cookies)
        cookies_button.click()
    except NoSuchElementException:
        logging.info("No cookies button found")