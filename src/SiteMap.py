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
        self.visited_urls = {}
        self.parallel_documents = []
        response = requests.get(self.map_url)
        root = etree.fromstring(response.content)
        for sitemap in root:
            children = sitemap.getchildren()
            self.visited_urls[children[0].text] = False
        if exclude is not None:
            for ex in exclude:
                self.visited_urls = {url: False for url in self.visited_urls.keys() if ex not in url}
        logging.info(f"Collected {len(self.visited_urls)} from site map")

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
            f.write(json.dumps(self.visited_urls))
        logging.info(f"Saved {len([key for key in self.visited_urls.keys() if self.visited_urls[key]])} visited urls to disk")

    def load_visited_urls_from_disk(self, loc: str) -> None:
        with open(loc) as f:
            self.visited_urls = json.loads(f.read())
        logging.info(f"Loaded {len([key for key in self.visited_urls.keys() if self.visited_urls[key]])} visited urls from file")