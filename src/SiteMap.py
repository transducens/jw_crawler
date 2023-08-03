import json
import requests
from src.ParallelDocument import ParallelDocument
from src.util import *
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver


class SiteMap:

    def __init__(self,
                 url: str,
                 exclude: List[str] = None):
        self.map_url = url
        self.urls = {}
        self.parallel_documents = []
        response = requests.get(self.map_url)
        root = etree.fromstring(response.content)
        for sitemap in root:
            children = sitemap.getchildren()
            self.urls[children[0].text] = False
        if exclude is not None:
            for ex in exclude:
                self.urls = {url: False for url in self.urls.keys() if ex not in url}

    @staticmethod
    def save_parallel_documents_to_disk(self, loc: str = None) -> None:
        d = {}
        for parallel_doc in self.parallel_documents:
            d[parallel_doc.url] = {"langs": parallel_doc.langs, "main_lang": parallel_doc.main_lang}
        if loc is None:
            loc = "parallel_docs.json"
        with open(loc, "w") as f:
            f.write(json.dumps(d))

    @staticmethod
    def load_parallel_documents_from_disk(self, loc: str) -> None:
        with open(loc) as f:
            parallel_docs = json.loads(f.read())
        self.parallel_documents = [ParallelDocument(
            url=key,
            langs=parallel_docs[key]["langs"],
            main_lang=parallel_docs[key]["main_lang"]
        ) for key in parallel_docs.keys()]

    @staticmethod
    def save_visited_urls_to_disk(self, loc: str = None) -> None:
        if loc is None:
            loc = "crawled_urls.json"
        with open(loc, "w") as f:
            f.write(json.dumps(self.urls))

    @staticmethod
    def load_visited_urls_from_disk(self, loc: str) -> None:
        with open(loc) as f:
            self.urls = json.loads(f.read())

    def get_parallel_documents(self, driver: webdriver):
        for url in self.urls.keys():
            driver.get(url)
            langs = []
            for language in LANGS:
                try:
                    language_input = driver.find_element(By.XPATH, ".//input[@id='otherAvailLangsChooser']")
                    language_input.clear()
                    language_input.send_keys(language)
                    sleep(1)
                    try:
                        driver.find_element(By.XPATH, f".//li[@data-value='{language}']")
                        langs.append(language)
                    except NoSuchElementException:
                        logging.debug(f"'{language}' not found in document")
                except NoSuchElementException:
                    logging.info(f"No parallel document at {url}")
            if len(langs) != 0:
                self.parallel_documents.append(ParallelDocument(
                    url=url,
                    langs=langs
                ))
            else:
                logging.debug(f"Parallel document at {url} does not contain Mayan languages")
            self.urls[url] = True

