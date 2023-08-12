import argparse
import json
import os

from src.Crawler import Crawler, logging
from src.SiteMap import SiteMap


def check_for_existing_save_file(save_file: str) -> None:
    delete_file = input(f"'{save_file}' exists and would be overwritten. "
                                      f"Continue? (y/n)")
    while ((delete_file == "y") or (delete_file == "n")) is False:
        delete_file = input("Please enter 'y' or 'n'")

    if delete_file == "y":
        os.remove(f"{save_file}")
    else:
        exit(0)


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
parser.add_argument("--site_map_url", help="Sets URL of site map to be downloaded before beginning"
                                                          "crawl operation")
parser.add_argument("--working_dir", default=".", help="Sets working directory. Default is the same directory as "
                                                       "script")
parser.add_argument("--main_language", help="Sets main language, which must correspond to site map language.",
                    default="es")
parser.add_argument("--languages", help="Sets languages to look for during crawl and scrape", default="es cak kek mam "
                                                                                                      "ctu quc poh tzh "
                                                                                                      "tzo yua")
parser.add_argument("--load_parallel_docs", action='store_true', help="Loads saved list of parallel docs.",
                    default=False)
parser.add_argument("--load_visited_urls", action='store_true', help="Loads saved list of visited urls", default=False)
parser.add_argument("--parallel_docs_save_interval", default=50, type=int, help="Sets how often to save parallel docs")
parser.add_argument("--parallel_texts_save_interval", default=50, type=int, help="Sets how often to save parallel"
                                                                                 " docs after being scraped")
parser.add_argument("--max_number_parallel_docs", default=0, type=int, help="Sets max number of parallel docs to "
                                                                            "gather")
parser.add_argument("--exclude", help="String containing tokens to exclude from site map separated by spaces",
                    default=None)
parser.add_argument("--snap", action='store_true', default=False, help="Include if using the Snap version of Firefox")

args = parser.parse_args()

langs = args.languages.split()

if args.crawl is False and args.scrape is False:
    logging.warning("You must select an operation, either --crawl or --scrape. Exiting.")
    exit(1)

if args.load_parallel_docs is False and os.path.exists(f"{args.working_dir}/parallel_documents.json"):
    check_for_existing_save_file(f"{args.working_dir}/parallel_documents.json")

if args.load_visited_urls is False and os.path.exists(f"{args.working_dir}/visited_urls.json"):
    check_for_existing_save_file(f"{args.working_dir}/visited_urls.json")

if args.crawl:
    if args.load_visited_urls:
        with open(f"{args.working_dir}/visited_urls.json") as f:
            visited_urls = json.loads(f.read())

    crawler = Crawler(
        site_map=SiteMap(
            url=args.site_map_url,
            exclude=args.exclude.split(" "),
            main_language=args.main_language,
            visited_urls=visited_urls if args.load_visited_urls else None,
        ),
        working_dir=args.working_dir,
        snap=args.snap,
        langs=langs,
    )

    crawler.crawl(
        parallel_documents_save_interval=args.parallel_docs_save_interval,
        load_parallel_docs=args.load_parallel_docs,
        load_visited_urls=args.load_visited_urls,
        max_number_parallel_docs=args.max_number_parallel_docs,
    )

if args.scrape:

    crawler = Crawler(
        site_map=None,
        working_dir=args.working_dir,
        snap=args.snap,
        langs=langs,
    )

    crawler.scrape(
        parallel_texts_save_interval=args.parallel_texts_save_interval
    )

logging.info("Finished")
