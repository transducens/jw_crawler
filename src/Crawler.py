import logging

from src.ParallelDocument import ParallelDocument
from src.SiteMap import SiteMap
from src.util import *
from selenium.webdriver.firefox.service import Service


class Crawler:
    def __init__(self,
                 site_map: SiteMap,
                 working_dir: str,
                 snap: bool,
                 ):
        self.site_map = site_map
        self.parallel_documents: List[ParallelDocument] = []
        self.working_dir = working_dir

        options = Options()
        options.add_argument("--headless")
        if snap:
            options.add_argument("--no-sandbox")
            geckodriver_path = "/snap/bin/geckodriver"
            driver_service = Service(executable_path=geckodriver_path)
            self.driver = webdriver.Firefox(options=options, service=driver_service)
        else:
            self.driver = webdriver.Firefox(options=options)

    def save_parallel_documents_to_disk(self) -> None:
        d = {}
        for parallel_doc in self.parallel_documents:
            d[parallel_doc.url] = {
                "langs": parallel_doc.langs,
                "main_lang": parallel_doc.main_lang,
                "is_scraped": parallel_doc.is_scraped
            }
        if not os.path.isdir(self.working_dir):
            os.mkdir(self.working_dir)

        with open(f"{self.working_dir}/parallel_documents.json", "w") as f:
            f.write(json.dumps(d))
        logging.info(f"Saving new parallel documents to disk.")

    def load_parallel_documents_from_disk(self) -> None:
        try:
            with open(f"{self.working_dir}/parallel_documents.json") as f:
                parallel_docs = json.loads(f.read())
        except FileNotFoundError:
            logging.warning(f"No parallel documents file found at {self.working_dir}/. Exiting.")
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
            f.write(json.dumps(self.site_map.visited_urls))
        logging.info(
            f"Saved {len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key]])} "
            f"visited urls to disk"
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

    def gather_parallel_documents(self, driver: webdriver,
                                  save_interval: int,
                                  load_parallel_docs: bool,
                                  load_visited_urls: bool,
                                  max_number: int):

        if load_visited_urls:
            self.load_visited_urls_from_disk()

        if load_parallel_docs:
            self.load_parallel_documents_from_disk()
            if len(self.parallel_documents) >= max_number:
                logging.info(f"Reached max number of documents to gather: {max_number}. Stopping crawl.")

        urls_to_visit = list(self.site_map.visited_urls.keys())
        urls_to_visit = [url for url in urls_to_visit if self.site_map.visited_urls[url] is False]

        for idx, url in enumerate(urls_to_visit):

            driver.get(url)
            logging.info(f"Crawling {url}")
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
                    logging.debug(f"No parallel document at {url}")

            if len(langs) != 0 and langs != [self.site_map.main_language]:
                self.parallel_documents.append(
                    ParallelDocument(
                        url=url,
                        langs=langs
                    )
                )
                logging.info(f"Added parallel document at {url} containing {str(langs)}")
                if max_number != 0 and len(self.parallel_documents) >= max_number:
                    logging.info(f"Reached max number of documents to gather: {max_number}. Stopping crawl.")
                    break
            else:
                logging.debug(f"Parallel document at {url} does not contain Mayan languages")

            self.site_map.visited_urls[url] = True

            if idx % save_interval == 0 and idx != 0:
                self.save_parallel_documents_to_disk()
                self.save_visited_urls_to_disk()

        logging.info("Finishing crawl and saving.")
        self.save_visited_urls_to_disk()
        self.save_parallel_documents_to_disk()

    def collect_parallel_texts(self, driver: webdriver,
                               save_interval: int,
                               ):

        if not os.path.isdir(f"{self.working_dir}/dataframes/"):
            logging.info(f"Creating directory to save dataframes at {self.working_dir}/dataframes/")
            os.mkdir(f"{self.working_dir}/dataframes/")

        self.load_parallel_documents_from_disk()

        logging.info("Begin scraping docs for parallel texts")
        parallel_documents_to_scrape = [doc for doc in self.parallel_documents if doc.is_scraped is False]
        for idx, parallel_document in enumerate(parallel_documents_to_scrape):
            doc_name = parallel_document.url.split("/")
            doc_name = [token for token in doc_name if token != '']
            doc_name = doc_name[-1]
            parallel_text_df = parallel_document.get_parallel_texts(driver)
            parallel_text_df.to_csv(f"{self.working_dir}/dataframes/{doc_name}.tsv", sep="\t")
            logging.info(
                f"Saved parallel text dataframe at {self.working_dir}/dataframes/{doc_name}.tsv containing languages: "
                f"{parallel_document.langs}."
            )
            parallel_document.is_scraped = True
            if idx % save_interval == 0 and idx != 0:
                n_docs_scraped = abs(len(parallel_documents_to_scrape) - idx)
                logging.info(f"Scraped {n_docs_scraped} new parallel documents.")
                self.save_parallel_documents_to_disk()
        logging.info("Finishing scrape and saving.")
        self.save_parallel_documents_to_disk()

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
