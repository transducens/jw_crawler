import logging
import json
import os
import pandas as pd
import uuid
from time import time
from typing import List, Optional, Tuple
from datetime import timedelta
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox import webdriver
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from src.ParallelDocument import ParallelDocument
from src.SiteMap import SiteMap
from selenium.webdriver.firefox.service import Service

log_format = (
    '[%(asctime)s] %(levelname)-8s %(message)s')

logging.basicConfig(
    level=logging.INFO,
    format=log_format,
    filename="crawl.log"
)


class Crawler:
    def __init__(self,
                 site_map: Optional[SiteMap],
                 working_dir: str,
                 snap: bool,
                 langs: List[str]
                 ):
        self.site_map = site_map
        self.parallel_documents: List[ParallelDocument] = []
        self.working_dir = working_dir
        self.langs = langs
        self.snap = snap
        self.starting_time: time = None
        self.elapsed_time: time = None
        self.driver = self.get_new_driver(snap=self.snap)

    def save_parallel_documents_to_disk(self, suppress_log: bool = False) -> None:
        d = {"starting_time": self.starting_time, "elapsed_time": time()}
        for parallel_doc in self.parallel_documents:
            d[parallel_doc.url] = {
                "langs": parallel_doc.langs,
                "main_lang": parallel_doc.main_lang,
                "is_scraped": parallel_doc.is_scraped,
                "uuid": str(parallel_doc.uuid)
            }
        if not os.path.isdir(self.working_dir):
            os.mkdir(self.working_dir)

        if os.path.exists(f"{self.working_dir}/parallel_documents.json"):
            with open(f"{self.working_dir}/parallel_documents.json") as f:
                n_parallel_docs_on_disk = [key for key in json.loads(f.read()).keys() if
                                           (key != 'elapsed_time') and (key != 'starting_time')]
                n_parallel_docs_on_disk = len(n_parallel_docs_on_disk)

        else:
            n_parallel_docs_on_disk = 0

        n_new_parallel_docs = abs(len(self.parallel_documents) - n_parallel_docs_on_disk)

        with open(f"{self.working_dir}/parallel_documents.json", "w") as f:
            f.write(json.dumps(d))

        if suppress_log is False:
            logging.info(f"{n_new_parallel_docs} new parallel documents saved")
            logging.info(f"{len(self.parallel_documents)} total parallel documents")

    def load_parallel_documents_from_disk(self) -> None:
        try:
            with open(f"{self.working_dir}/parallel_documents.json") as f:
                d = json.loads(f.read())
        except FileNotFoundError:
            logging.warning(f"No parallel documents file found in working directory. Exiting.")
            exit(1)

        self.starting_time = d['starting_time']
        self.elapsed_time = d['elapsed_time']

        self.parallel_documents = [
            ParallelDocument(
                url=key,
                langs=d[key]["langs"],
                main_lang=d[key]["main_lang"],
                is_scraped=d[key]["is_scraped"],
                uuid=uuid.UUID(d[key].get("uuid")) if d[key].get("uuid") is not None else None 
            ) for key in d.keys() if key != 'starting_time' and key != 'elapsed_time'
        ]
        logging.info(f"Loaded {len(self.parallel_documents)} parallel documents from disk")

    def save_visited_urls_to_disk(self) -> None:

        if not os.path.isdir(self.working_dir):
            os.mkdir(self.working_dir)

        with open(f"{self.working_dir}/visited_urls.json", "w") as f:
            f.write(json.dumps(self.site_map.visited_urls))

        logging.info(
            f"{len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key] is True])}"
            f"/{len(self.site_map.visited_urls)} URLs crawled"
        )

    def load_visited_urls_from_disk(self) -> None:

        try:
            with open(f"{self.working_dir}/visited_urls.json") as f:
                self.site_map.visited_urls = json.loads(f.read())
        except FileNotFoundError:
            logging.warning(f"No visited urls file found at {self.working_dir}/. Exiting.")
            exit(1)

        logging.info(
            f"Loaded {len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key]])} "
            f"visited urls from file"
        )

    def crawl(self,
              save_interval: int,
              load_parallel_docs: bool,
              load_visited_urls: bool,
              max_number: int) -> None:

        self.starting_time = time()

        if load_visited_urls:
            self.load_visited_urls_from_disk()

        if load_parallel_docs:
            self.load_parallel_documents_from_disk()
            if len(self.parallel_documents) >= max_number != 0:
                logging.info(f"Reached max number of documents to gather: {max_number}. Stopping crawl.")

        urls_to_visit = list(self.site_map.visited_urls.keys())
        urls_to_visit = [url for url in urls_to_visit if self.site_map.visited_urls[url] is False]

        for idx, url in enumerate(urls_to_visit):
            self.driver.get(url)
            logging.info(f"Crawling {url}")
            langs = []
            for language in self.langs:
                try:
                    language_input = self.driver.find_element(By.XPATH, ".//input[@id='otherAvailLangsChooser']")
                    language_input.clear()
                    language_input.send_keys(language)
                    ParallelDocument.wait_for_language_to_load(self.driver)
                    try:
                        self.driver.find_element(By.XPATH, f".//li[@data-value='{language}']")
                        langs.append(language)
                    except NoSuchElementException:
                        logging.debug(f"'{language}' not found in document")
                except NoSuchElementException:
                    logging.debug(f"No parallel document at {url}")

            if len(langs) != 0 and langs != [self.site_map.main_language]:
                self.parallel_documents.append(
                    ParallelDocument(
                        url=url,
                        langs=langs
                    )
                )
                logging.info(f"Added parallel document: {str(langs)}")
                if max_number != 0 and len(self.parallel_documents) >= max_number:
                    logging.info(f"Reached max number of documents to gather: {max_number}. Stopping crawl.")
                    break
            else:
                logging.debug(f"Parallel document at {url} does not contain Mayan languages")

            self.site_map.visited_urls[url] = True

            if idx % save_interval == 0 and idx != 0:
                self.save_parallel_documents_to_disk()
                self.save_visited_urls_to_disk()
                self.driver.delete_all_cookies()

        if self.elapsed_time is None:
            self.elapsed_time = time()
        elapsed_time = abs(int(self.elapsed_time - self.starting_time))
        logging.info(f"Finished crawling in {timedelta(seconds=elapsed_time)}. Saving.")
        self.starting_time = None
        self.elapsed_time = None
        self.save_visited_urls_to_disk()
        self.save_parallel_documents_to_disk()
        logging.info("Done.")

    def scrape(self,
               save_interval: int,
               rescrape: bool
               ) -> None:

        if not os.path.isdir(f"{self.working_dir}/dataframes/"):
            logging.info(f"Creating directory to save dataframes at {self.working_dir}/dataframes/")
            os.mkdir(f"{self.working_dir}/dataframes/")

        self.driver.delete_all_cookies()

        self.load_parallel_documents_from_disk()

        if self.starting_time is None:
            self.starting_time = time()

        if rescrape is True:
            for doc in self.parallel_documents:
                doc.is_scraped = False

        logging.info("Begin scraping docs for parallel texts")

        parallel_documents_to_scrape = [doc for doc in self.parallel_documents if doc.is_scraped is False]
        for idx, parallel_document in enumerate(parallel_documents_to_scrape):

            doc_name = parallel_document.uuid
            parallel_text_df = parallel_document.get_parallel_texts(self.driver)

            is_valid, valid_msg = self.validate_dataframe(parallel_text_df, parallel_document.langs)
            if is_valid is True:
                parallel_text_df.to_csv(f"{self.working_dir}/dataframes/{doc_name}.tsv", sep="\t")
                logging.info(
                    f"New dataframe from {parallel_document.url}: "
                    f"{parallel_document.langs}."
                )
                parallel_document.is_scraped = True
            else:
                logging.warning(f"Failed to scrape parallel document at {parallel_document.url}: {valid_msg}")
                parallel_document.is_scraped = False

            if idx % save_interval == 0 and idx != 0:
                n_docs_scraped = len([doc for doc in self.parallel_documents if doc.is_scraped is True])
                logging.info(f"{n_docs_scraped}/{len(self.parallel_documents)} parallel documents scraped. "
                             f"Updating parallel documents status to 'scraped'")
                self.save_parallel_documents_to_disk(suppress_log=True)
                self.driver.delete_all_cookies()

        logging.info("Finishing scrape and saving.")

        n_unscraped = len([doc for doc in self.parallel_documents if doc.is_scraped is False])
        if n_unscraped != 0:
            logging.warning(f"{n_unscraped} unscraped parallel documents on disk")

        if self.elapsed_time == 0:
            self.elapsed_time = time()
        elapsed_time = abs(int(self.elapsed_time - self.starting_time))
        logging.info(f"Finished scraping in {timedelta(seconds=elapsed_time)}. Saving.")
        self.starting_time = None
        self.elapsed_time = None
        self.save_parallel_documents_to_disk(suppress_log=True)
        logging.info("Done.")

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, langs: List[str]) -> Tuple[bool, str]:

        if df is None:
            return False, "Dataframe is 'None'"

        if df.empty is True:
            return False, "Dataframe is empty."

        if df.isna().values.any() is True:
            return False, "Null values in dataframe."

        langs_in_df = [lang for lang in df.columns.values]
        for lang in langs:
            if lang not in langs_in_df:
                return False, "Missing languages in dataframe."

        return True, ""

    @staticmethod
    def get_new_driver(snap: bool = False) -> webdriver.Firefox:
        options = Options()
        options.add_argument("--headless")
        if snap:
            options.add_argument("--no-sandbox")
            geckodriver_path = "/snap/bin/geckodriver"
            driver_service = Service(executable_path=geckodriver_path)
            return webdriver.Firefox(options=options, service=driver_service)
        return webdriver.Firefox(options=options)
