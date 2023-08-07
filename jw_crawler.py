from src.Crawler import Crawler
from src.SiteMap import SiteMap
from src.util import *

parser = argparse.ArgumentParser(
    prog="jw_crawler",
    description="Crawl the website jw.org for Mayan languages",
    epilog="Inspired by the tireless efforts of the JW300 team"
)

parser.add_argument("-c", "--crawl", action='store_true', default=False, help="Runs crawl operation, which gathers "
                                                                              "parallel documents from JW.org")
parser.add_argument("-s", "--scrape", action='store_true', default=False, help="Runs scrape operation, which extracts"
                                                                               "parallel text from parallel documents"
                                                                               "and saves them as dataframes")
parser.add_argument("--site_map_url", required=True, help="Sets URL of site map to be downloaded before beginning"
                                                          "crawl operation")
parser.add_argument("--working_dir", default=".", help="Sets working directory. Default is the same directory as "
                                                       "script")
parser.add_argument("--load_parallel_docs", action='store_true', help="Loads saved list of parallel docs.")
parser.add_argument("--load_visited_urls", action='store_true', help="Loads saved list of visited urls")
parser.add_argument("--parallel_docs_save_interval", default=50, type=int, help="Sets how often to save parallel docs")
parser.add_argument("--parallel_texts_save_interval", default=50, type=int, help="Sets how often to save parallel"
                                                                                 "docs after being scraped")
parser.add_argument("--max_number_parallel_docs", default=0, type=int, help="Sets max number of parallel docs to "
                                                                            "gather")
parser.add_argument("--exclude", help="Pass a string containing tokens to exclude from site map separated by spaces")
parser.add_argument("--snap", action='store_true', default=False, help="Use if using the Snap version of Firefox")

args = parser.parse_args()

if args.crawl is False and args.scrape is False:
    logging.warning("You must select an operation, either --crawl or --scrape. Exiting.")
    exit(1)

if args.load_visited_urls:
    with open(f"{args.working_dir}/visited_urls.json") as f:
        visited_urls = json.loads(f.read())

crawler = Crawler(
    site_map=SiteMap(
        url=args.site_map_url,
        exclude=args.exclude.split(" "),
        visited_urls=visited_urls if args.load_visited_urls else None
    ),
    working_dir=args.working_dir,
    snap=args.snap,
)

if args.crawl:
    crawler.crawl(
        parallel_documents_save_interval=args.parallel_docs_save_interval,
        load_parallel_docs=args.load_parallel_docs,
        load_visited_urls=args.load_visited_urls,
        max_number_parallel_docs=args.max_number_parallel_docs,
    )

if args.scrape:
    crawler.scrape(
        parallel_texts_save_interval=args.parallel_texts_save_interval
    )

logging.info("Finished")
