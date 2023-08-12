import logging
import json
import os
from time import sleep, time
from typing import List
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
                 site_map: SiteMap,
                 working_dir: str,
                 snap: bool,
                 langs: List[str]
                 ):
        self.site_map = site_map
        self.parallel_documents: List[ParallelDocument] = []
        self.working_dir = working_dir
        self.langs = langs
        self.snap = snap
        self.starting_time: time = time()
        self.elapsed_time: time = 0
        self.driver = self.get_new_driver(snap=self.snap)

    def save_parallel_documents_to_disk(self, suppress_log: bool = False) -> None:
        d = {}
        for parallel_doc in self.parallel_documents:
            d[parallel_doc.url] = {
                "langs": parallel_doc.langs,
                "main_lang": parallel_doc.main_lang,
                "is_scraped": parallel_doc.is_scraped
            }
        if not os.path.isdir(self.working_dir):
            os.mkdir(self.working_dir)

        if os.path.exists(f"{self.working_dir}/parallel_documents.json"):
            with open(f"{self.working_dir}/parallel_documents.json") as f:
                n_parallel_docs_on_disk = json.loads(f.read())
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
                parallel_docs = json.loads(f.read())
        except FileNotFoundError:
            logging.warning(f"No parallel documents file found in working directory. Exiting.")
            exit(1)
        self.parallel_documents = [
            ParallelDocument(
                url=key,
                langs=parallel_docs[key]["langs"],
                main_lang=parallel_docs[key]["main_lang"],
                is_scraped=parallel_docs[key]["is_scraped"],
            ) for key in parallel_docs.keys()
        ]
        logging.info(f"Loaded {len(self.parallel_documents)} parallel documents from disk")

    def save_visited_urls_to_disk(self) -> None:

        if not os.path.isdir(self.working_dir):
            os.mkdir(self.working_dir)

        with open(f"{self.working_dir}/visited_urls.json", "w") as f:
            self.site_map.visited_urls["starting_time"] = self.starting_time
            self.site_map.visited_urls["elapsed_time"] = time()
            f.write(json.dumps(self.site_map.visited_urls))
            del self.site_map.visited_urls["starting_time"]
            del self.site_map.visited_urls["elapsed_time"]

        logging.info(
            f"{len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key] is True])}"
            f"/{len(self.site_map.visited_urls)} URLs crawled"
        )

    def load_visited_urls_from_disk(self) -> None:

        try:
            with open(f"{self.working_dir}/visited_urls.json") as f:
                self.site_map.visited_urls = json.loads(f.read())
                self.starting_time = self.site_map.visited_urls["starting_time"]
                self.elapsed_time = self.site_map.visited_urls["elapsed_time"]
                del self.site_map.visited_urls["starting_time"]
                del self.site_map.visited_urls["elapsed_time"]
        except FileNotFoundError:
            logging.warning(f"No visited urls file found at {self.working_dir}/. Exiting.")
            exit(1)

        logging.info(
            f"Loaded {len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key]])} "
            f"visited urls from file"
        )

    def gather_parallel_documents(self, driver: webdriver,
                                  save_interval: int,
                                  load_parallel_docs: bool,
                                  load_visited_urls: bool,
                                  max_number: int):

        if load_visited_urls:
            self.load_visited_urls_from_disk()

        if load_parallel_docs:
            self.load_parallel_documents_from_disk()
            if len(self.parallel_documents) >= max_number != 0:
                logging.info(f"Reached max number of documents to gather: {max_number}. Stopping crawl.")

        urls_to_visit = list(self.site_map.visited_urls.keys())
        urls_to_visit = [url for url in urls_to_visit if self.site_map.visited_urls[url] is False]

        self.starting_time = time()

        for idx, url in enumerate(urls_to_visit):
            driver.get(url)
            logging.info(f"Crawling {url}")
            langs = []
            for language in self.langs:
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

        logging.info("Finishing crawl and saving.")
        self.save_visited_urls_to_disk()
        self.save_parallel_documents_to_disk()
        if self.elapsed_time == 0:
            self.elapsed_time = time()
        elapsed_time = int(self.elapsed_time - self.starting_time)
        logging.info(f"Finished crawl in {timedelta(seconds=elapsed_time)}")

    def collect_parallel_texts(self, driver: webdriver,
                               save_interval: int,
                               ):

        if not os.path.isdir(f"{self.working_dir}/dataframes/"):
            logging.info(f"Creating directory to save dataframes at {self.working_dir}/dataframes/")
            os.mkdir(f"{self.working_dir}/dataframes/")
        self.driver.delete_all_cookies()
        self.load_parallel_documents_from_disk()
        logging.info("Begin scraping docs for parallel texts")
        parallel_documents_to_scrape = [doc for doc in self.parallel_documents if doc.is_scraped is False]
        for idx, parallel_document in enumerate(parallel_documents_to_scrape):
            doc_name = parallel_document.url.split("org")[1]
            doc_name = doc_name.replace("/", "_")
            parallel_text_df = parallel_document.get_parallel_texts(driver)
            parallel_text_df.to_csv(f"{self.working_dir}/dataframes/{doc_name}.tsv", sep="\t")
            logging.info(
                f"New parallel text dataframe: {self.working_dir}/dataframes/{doc_name}.tsv containing languages: "
                f"{parallel_document.langs}."
            )
            parallel_document.is_scraped = True
            if idx % save_interval == 0 and idx != 0:
                n_docs_scraped = len([doc for doc in self.parallel_documents if doc.is_scraped is True])
                logging.info(f"{n_docs_scraped}/{len(self.parallel_documents)} parallel documents scraped. "
                             f"Updating parallel documents status to 'scraped'")
                self.save_parallel_documents_to_disk(suppress_log=True)
        logging.info("Finishing scrape and saving.")
        self.save_parallel_documents_to_disk(suppress_log=True)

    def crawl(self,
              parallel_documents_save_interval: int,
              load_parallel_docs: bool,
              load_visited_urls: bool,
              max_number_parallel_docs: int,
              ):

        self.gather_parallel_documents(driver=self.driver,
                                       save_interval=parallel_documents_save_interval,
                                       load_parallel_docs=load_parallel_docs,
                                       load_visited_urls=load_visited_urls,
                                       max_number=max_number_parallel_docs
                                       )

    def scrape(self, parallel_texts_save_interval: int):

        self.collect_parallel_texts(driver=self.driver,
                                    save_interval=parallel_texts_save_interval,
                                    )

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

