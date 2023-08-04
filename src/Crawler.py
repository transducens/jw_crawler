from src.ParallelDocument import ParallelDocument
from src.SiteMap import SiteMap
from src.util import *


class Crawler:
    def __init__(self, site_map: SiteMap):
        self.site_map = site_map
        self.parallel_documents: List[ParallelDocument] = []

    def save_parallel_documents_to_disk(self, loc: str = None) -> None:
        d = {}
        for parallel_doc in self.parallel_documents:
            d[parallel_doc.url] = {"langs": parallel_doc.langs, "main_lang": parallel_doc.main_lang}
        if loc is None:
            loc = "parallel_docs.json"
        with open(loc, "w") as f:
            f.write(json.dumps(d))
        logging.info(f"Saved {len(self.parallel_documents)} parallel documents to disk")

    def load_parallel_documents_from_disk(self, loc: str) -> None:
        with open(loc) as f:
            parallel_docs = json.loads(f.read())
        self.parallel_documents = [
            ParallelDocument(
                url=key,
                langs=parallel_docs[key]["langs"],
                main_lang=parallel_docs[key]["main_lang"]
            ) for key in parallel_docs.keys()
        ]
        logging.info(f"Loaded {len(self.parallel_documents)} parallel documents from disk")

    def save_visited_urls_to_disk(self, loc: str = None) -> None:
        if loc is None:
            loc = "visited_urls.json"
        with open(loc, "w") as f:
            f.write(json.dumps(self.site_map.visited_urls))
        logging.info(
            f"Saved {len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key]])} "
            f"visited urls to disk"
        )

    def load_visited_urls_from_disk(self, loc: str) -> None:
        with open(loc) as f:
            self.site_map.visited_urls = json.loads(f.read())
        logging.info(
            f"Loaded {len([key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key]])} "
            f"visited urls from file"
        )

    def gather_parallel_documents(self, driver: webdriver,
                                  save_interval: int = 50,
                                  visited_urls_file: str = None,
                                  parallel_documents_file: str = None):

        if visited_urls_file is not None:
            self.load_visited_urls_from_disk(visited_urls_file)

        if parallel_documents_file is not None:
            self.load_parallel_documents_from_disk(parallel_documents_file)

        for idx, url in enumerate(key for key in self.site_map.visited_urls.keys() if
                                  self.site_map.visited_urls[key] is False):
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
            if langs != [self.site_map.main_language]:
                self.parallel_documents.append(
                    ParallelDocument(
                        url=url,
                        langs=langs
                    )
                )
                logging.info(f"Added parallel document at {url} containing {str(langs)}")
            else:
                logging.debug(f"Parallel document at {url} does not contain Mayan languages")
            self.site_map.visited_urls[url] = True
            if idx % save_interval == 0 and idx != 0:
                self.save_parallel_documents_to_disk()
                self.save_visited_urls_to_disk()

        self.save_visited_urls_to_disk()
        self.save_parallel_documents_to_disk()
