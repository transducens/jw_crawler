from src.ParallelDocument import ParallelDocument
from src.SiteMap import SiteMap
from src.util import *


class Crawler:
    def __init__(self, site_map: SiteMap):
        self.site_map = site_map

    def gather_parallel_documents(self, driver: webdriver,
                                  save_interval: int = 50,
                                  visited_urls_file: str = None,
                                  parallel_documents_file: str = None):

        if visited_urls_file is not None:
            self.site_map.load_visited_urls_from_disk(visited_urls_file)

        if parallel_documents_file is not None:
            self.site_map.load_parallel_documents_from_disk(parallel_documents_file)

        for idx, url in enumerate(key for key in self.site_map.visited_urls.keys() if self.site_map.visited_urls[key] is False):
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
            if len(langs) != 0 or langs != ['es']:
                self.site_map.parallel_documents.append(
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
                self.site_map.save_parallel_documents_to_disk()
                self.site_map.save_visited_urls_to_disk()

        self.site_map.save_visited_urls_to_disk()
        self.site_map.save_parallel_documents_to_disk()
