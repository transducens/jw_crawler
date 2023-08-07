from src.Crawler import Crawler
from src.SiteMap import SiteMap
from src.util import *

parser = argparse.ArgumentParser(
    prog="jw_crawler",
    description="Crawl the website jw.org for Mayan languages",
    epilog="Inspired by the tireless efforts of the JW300 team"
)

parser.add_argument("-c", "--crawl", action='store_true', default=False)
parser.add_argument("-s", "--scrape", action='store_true', default=False)
parser.add_argument("--site_map_url", required=True)
parser.add_argument("--working_dir", default=".")
parser.add_argument("--load_parallel_docs", action='store_true')
parser.add_argument("--load_visited_urls", action='store_true')
parser.add_argument("--parallel_docs_save_interval", default=50, type=int)
parser.add_argument("--parallel_texts_save_interval", default=50, type=int)
parser.add_argument("--max_number_parallel_docs", default=0, type=int)
parser.add_argument("--exclude", help="Pass a string containing tokens to exclude from site map separated by spaces")

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
    working_dir=args.working_dir
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
