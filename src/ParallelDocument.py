import base64
import pandas as pd
from time import sleep
from typing import List, Tuple, Union
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from selenium.webdriver.remote.webelement import WebElement

from src.Crawler import logging


class ParallelDocument:

    def __init__(self, url: str, langs: List[str], main_lang: str = "es", is_scraped: bool = False):
        self.url = url
        self.langs = langs
        self.main_lang = main_lang
        self.df: pd.DataFrame = pd.DataFrame()
        self.is_scraped = is_scraped

    @staticmethod
    def wait_for_language_to_load(driver: webdriver) -> None:
        loading: bool = True
        while loading is True:
            try:
                x_path_exp = ".//div[@class='loadingIndicator']//ancestor::div[@id='jsFullScreenLoadingIndicator']"
                driver.find_element(By.XPATH, x_path_exp)
                sleep(1)
            except NoSuchElementException:
                loading = False

    def go_to_lang(self, lang: str, driver: webdriver) -> None:
        if driver.current_url != self.url:
            driver.get(self.url)

        try:
            language_input = driver.find_element(By.XPATH, ".//input[@id='otherAvailLangsChooser']")
            language_input.clear()
            language_input.send_keys(lang)
            self.wait_for_language_to_load(driver)
            driver.find_element(By.XPATH, f".//li[@data-value='{lang}']")
            language_input.send_keys(Keys.ENTER)
            self.wait_for_language_to_load(driver)
        except NoSuchElementException:
            logging.warning(f"Language {lang} not found in parallel document {self.url}")

    def get_text_by_lang(self, lang: str, driver: webdriver) -> Union[pd.DataFrame, None]:

        def get_p_q_lists() -> Tuple[List[WebElement], List[WebElement]]:
            p = driver.find_elements(By.XPATH, ".//*[boolean(number(substring-after(@id, 'p')))]")
            q = driver.find_elements(By.XPATH, ".//*[boolean(number(substring-after(@id, 'q')))]")
            return p, q

        self.go_to_lang(lang, driver)
        attempt = 1

        while True:
            p_list, q_list = get_p_q_lists()
            if len(p_list) == 0 and len(q_list) == 0:
                logging.warning(f"{lang} not found in parallel document at {self.url}. Attempt {attempt}")
                driver.delete_all_cookes()
                driver.refresh()
                attempt += 1
                if attempt >= 3:
                    driver.save_screenshot(f"error_{lang}_{self.url}.png")
                    logging.warning(f"Language {lang} not found in parallel document. Saving screenshot.")
                    return None
            else:
                break

        p_text = [p.text for p in p_list if p.text != ""]
        p_indices = [f"p{x}" for x in range(1, len(p_text) + 1)]
        p_df = {lang: p_text}
        p_df = pd.DataFrame(p_df, index=p_indices)

        q_text = [q.text for q in q_list if q.text != ""]
        q_indices = [f"q{x}" for x in range(1, len(q_text) + 1)]
        q_df = {lang: q_text}
        q_df = pd.DataFrame(q_df, index=q_indices)

        return pd.concat([p_df, q_df], axis=0)

    def get_parallel_texts(self, driver) -> Union[pd.DataFrame, None]:
        try:
            dfs = [self.get_text_by_lang(lang=lang, driver=driver) for lang in self.langs]
            self.df = pd.concat(dfs, axis=1)
            self.df.index.name = self.url
            return self.df

        except Exception:
            logging.warning(f"Failed to scrape {self.url}")
            return None

    def save_dataframe(self) -> None:
        self.df.to_csv(f"{self.url}.csv")

    def get_encoded_url_string(self):
        url_string = self.url[:-1].encode('ASCII')
        url_string = base64.b64encode(url_string)
        return url_string.decode('ASCII')[-50:]
