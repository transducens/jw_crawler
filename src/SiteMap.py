from src.util import *


class SiteMap:

    def __init__(self,
                 url: str,
                 main_language: str = "es",
                 exclude: List[str] = None,
                 visited_urls: dict = None):
        self.map_url = url
        self.main_language = main_language
        self.visited_urls = {} if visited_urls is None else visited_urls
        if self.visited_urls == {}:
            response = requests.get(self.map_url)
            root = etree.fromstring(response.content)
            for sitemap in root:
                children = sitemap.getchildren()
                self.visited_urls[children[0].text] = False
        if exclude is not None:
            for ex in exclude:
                self.visited_urls = {url: False for url in self.visited_urls.keys() if ex not in url}
        logging.info(f"Collected {len(self.visited_urls)} urls from site map")