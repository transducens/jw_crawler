from time import sleep

import pandas as pd
from typing import List

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from src.Crawler import logging


class ParallelDocument:

    def __init__(self, url: str, langs: List[str], main_lang: str = "es", is_scraped: bool = False):
        self.url = url
        self.langs = langs
        self.main_lang = main_lang
        self.df: pd.DataFrame = pd.DataFrame()
        self.is_scraped = is_scraped

    def go_to_lang(self, lang: str, driver: webdriver) -> None:
        if driver.current_url != self.url:
            driver.get(self.url)

        try:
            language_input = driver.find_element(By.XPATH, ".//input[@id='otherAvailLangsChooser']")
            language_input.clear()
            language_input.send_keys(lang)
            driver.find_element(By.XPATH, f".//li[@data-value='{lang}']")
            sleep(1)
            language_input.send_keys(Keys.ENTER)
            sleep(1)
        except NoSuchElementException:
            logging.warning(f"Language {lang} not found in parallel document {self.url}")

    def get_text_by_lang(self, lang: str, driver: webdriver) -> pd.DataFrame:
        self.go_to_lang(lang, driver)
        p_list = driver.find_elements(By.XPATH, ".//*[boolean(number(substring-after(@id, 'p')))]")
        q_list = driver.find_elements(By.XPATH, ".//*[boolean(number(substring-after(@id, 'q')))]")
        if len(p_list) == 0 and len(q_list) == 0:
            logging.warning(f"Language {lang} not found in parallel document {self.url}")
            return pd.DataFrame()

        p_text = [p.text for p in p_list if p.text != ""]
        p_indices = [f"p{x}" for x in range(1, len(p_text) + 1)]
        p_df = {lang: p_text}
        p_df = pd.DataFrame(p_df, index=p_indices)

        q_text = [q.text for q in q_list if q.text != ""]
        q_indices = [f"q{x}" for x in range(1, len(q_text) + 1)]
        q_df = {lang: q_text}
        q_df = pd.DataFrame(q_df, index=q_indices)

        return pd.concat([p_df, q_df], axis=0)

    def get_parallel_texts(self, driver) -> pd.DataFrame:
        try:
            dfs = [self.get_text_by_lang(lang=lang, driver=driver) for lang in self.langs]
            self.df = pd.concat(dfs, axis=1)
            return self.df

        except Exception:
            logging.warning(f"Failed to scrape {self.url}")
            return pd.DataFrame()

    def save_dataframe(self) -> None:
        self.df.to_csv(f"{self.url}.csv")
