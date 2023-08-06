from src.ParallelDocument import ParallelDocument
from src.SiteMap import SiteMap
from src.util import *


class Crawler:
    def __init__(self,
                 site_map: SiteMap,
                 working_dir: str = "",
                 ):
        self.site_map = site_map
        self.parallel_documents: List[ParallelDocument] = []
        self.working_dir = working_dir

        options = webdriver.Options()
        options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

    def save_parallel_documents_to_disk(self, loc: str = ".") -> None:
        d = {}
        for parallel_doc in self.parallel_documents:
            d[parallel_doc.url] = {
                "langs": parallel_doc.langs,
                "main_lang": parallel_doc.main_lang,
                "is_scraped": parallel_doc.is_scraped
            }
        if loc is not None:
            os.mkdir(loc)

        with open(f"{loc}/parallel_documents.json", "w") as f:
            f.write(json.dumps(d))
        logging.info(f"Saving new parallel documents to disk.")

    def load_parallel_documents_from_disk(self, loc: str) -> None:
        with open(f"{loc}/parallel_documents.json") as f:
            parallel_docs = json.loads(f.read())
        self.parallel_documents = [
            ParallelDocument(
                url=key,
                langs=parallel_docs[key]["langs"],
                main_lang=parallel_docs[key]["main_lang"],
                is_scraped=parallel_docs[key]["is_scraped"],
            ) for key in parallel_docs.keys()
        ]
        logging.info(f"Loaded {len(self.parallel_documents)} parallel documents from disk")

    def save_visited_urls_to_disk(self, loc: str = None) -> None:
        if loc is not None:
            os.mkdir(loc)
        with open(f"{loc}/visited_urls.json", "w") as f:
            f.write(json.dumps(self.site_map.visited_urls))
        logging.info(
            f"Saved {len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key]])} "
            f"visited urls to disk"
        )

    def load_visited_urls_from_disk(self, loc: str) -> None:
        with open(f"{loc}/visited_urls.json") as f:
            self.site_map.visited_urls = json.loads(f.read())
        logging.info(
            f"Loaded {len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key]])} "
            f"visited urls from file"
        )

    def gather_parallel_documents(self, driver: webdriver,
                                  save_interval: int,
                                  visited_urls_file: str,
                                  parallel_documents_file: str,
                                  max_number: int):

        if visited_urls_file is not None:
            self.load_visited_urls_from_disk(visited_urls_file)

        if parallel_documents_file is not None:
            self.load_parallel_documents_from_disk(parallel_documents_file)
            if len(self.parallel_documents) >= max_number:
                logging.info(f"Reached max number of documents to gather: {max_number}. Stopping crawl.")

        urls_to_visit = list(self.site_map.visited_urls.keys())
        urls_to_visit = [url for url in urls_to_visit if self.site_map.visited_urls[url] is False]

        for idx, url in enumerate(urls_to_visit):

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
                    logging.debug(f"No parallel document at {url}")

            if len(langs) != 0 and langs != [self.site_map.main_language]:
                self.parallel_documents.append(
                    ParallelDocument(
                        url=url,
                        langs=langs
                    )
                )
                logging.info(f"Added parallel document at {url} containing {str(langs)}")
                if max_number is not None and len(self.parallel_documents) >= max_number:
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
                               loc: str,
                               save_interval: int):

        if not os.path.isdir(loc):
            os.mkdir(loc)

        parallel_documents_to_scrape = [doc for doc in self.parallel_documents if doc.is_scraped is False]
        for idx, parallel_document in enumerate(parallel_documents_to_scrape):
            doc_name = parallel_document.url.split("/")
            doc_name = [s for s in doc_name if s != '']
            doc_name = doc_name[-1]
            parallel_text_df = parallel_document.get_parallel_texts(driver)
            parallel_text_df.to_csv(f"{loc}/{doc_name}", sep="\t")
            logging.info(
                f"Saved parallel text dataframe at {loc}/{doc_name} containing languages: {parallel_document.langs}."
            )
            parallel_document.is_scraped = True
            if idx % save_interval == 0 and idx != 0:
                n_docs_scraped = abs(len(parallel_documents_to_scrape) - idx)
                logging.info(f"Scraped {n_docs_scraped} new parallel documents.")
                self.save_parallel_documents_to_disk()

    def crawl(self,
              parallel_documents_save_interval: int,
              visited_urls_file_loc: str,
              parallel_docs_file_loc: str,
              max_number_parallel_docs: int,
              parallel_corpus_dir_loc,
              parallel_texts_save_interval: int):

        self.gather_parallel_documents(driver=self.driver,
                                       save_interval=parallel_documents_save_interval,
                                       parallel_documents_file=parallel_docs_file_loc,
                                       visited_urls_file=visited_urls_file_loc,
                                       max_number=max_number_parallel_docs
                                       )
        self.collect_parallel_texts(driver=self.driver,
                                    loc=parallel_corpus_dir_loc,
                                    save_interval=parallel_texts_save_interval
                                    )
