import argparse
import json
import os

from src.crawler import Crawler
from src.sitemap import SiteMap


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

parser.add_argument("--working_dir", help="Sets working directory. Default: main language", default=""),
parser.add_argument("--rescrape", action='store_true', default=False, help="Rescrape all parallel documents on disk")
parser.add_argument("--main_language", required=True, help="Sets language for downloading the site map. Default: 'es'",
                    default="es")
parser.add_argument("--languages", required=True, help="Sets languages to look for during crawl and scrape")
parser.add_argument("-p", "--load_parallel_docs", action='store_true', help="Loads saved list of parallel docs.",
                    default=False)
parser.add_argument("-v", "--load_visited_urls", action='store_true', help="Loads saved list of visited urls",
                    default=False)
parser.add_argument("--save_interval", default=20, type=int, help="Sets how often to save parallel docs")
parser.add_argument("--max_number_parallel_docs", default=0, type=int, help="Sets max number of parallel docs to "
                                                                            "gather")
parser.add_argument("--exclude", help="String containing tokens to exclude from site map separated by spaces. Default:"
                                      " None",
                    default=None)
parser.add_argument("--snap", action='store_true', default=False, help="Include if using the Snap version of Firefox")
parser.add_argument("--allow_misalignments", action='store_true', default=False, help="Gather dataframes from parallel"
                                                                                      "documents whose paragraphs do "
                                                                                      "not align exactly across "
                                                                                      "languages. Reduces precision of "
                                                                                      "parallel texts. Default: False")

args = parser.parse_args()
if args.working_dir == "":
    args.working_dir = args.main_language

if args.crawl is True:

    if os.path.exists(args.working_dir) is False:
        os.mkdir(args.working_dir)

    if args.load_visited_urls is False:
        assert args.site_map_url is not None, "No site map specified. Either load visited urls file with -v or " \
                                              "specify the url of a site map"
        if os.path.exists(f"{args.working_dir}/visited_urls.json"):
            check_for_existing_save_file(f"{args.working_dir}/visited_urls.json")
    else:
        try:
            with open(f"{args.working_dir}/visited_urls.json") as f:
                visited_urls = json.loads(f.read())
        except FileNotFoundError as e:
            print(f"{e}. No 'visited_urls.json' file found in working dir. Use --site_map_url to fetch a new site map.")
            exit(1)

    if args.load_parallel_docs is False:
        if os.path.exists(f"{args.working_dir}/parallel_documents.json"):
            check_for_existing_save_file(f"{args.working_dir}/parallel_documents.json")
    else:
        assert os.path.exists(f"{args.working_dir}/parallel_documents.json"), f"No 'parallel_documents.json' file " \
                                                                              f"found."

    if os.path.exists(args.working_dir) is False:
        os.mkdir(args.working_dir)

    print("Crawling in progress. Refer to 'crawl.log' for updates.")
    
    crawler = Crawler(
        site_map=SiteMap(
            exclude=args.exclude.split(" ") if args.exclude is not None else None,
            main_language=args.main_language,
            visited_urls=visited_urls if args.load_visited_urls is True else None,
        ),
        working_dir=args.working_dir,
        snap=args.snap,
        langs=args.languages.split(),
    )

    crawler.crawl(
        save_interval=args.save_interval,
        load_parallel_docs=args.load_parallel_docs,
        load_visited_urls=args.load_visited_urls,
        max_number=args.max_number_parallel_docs,
    )

if args.scrape:
    assert os.path.exists(f"{args.working_dir}/parallel_documents.json"), f"'parallel_documents.json' not found in " \
                                                                          f"working directory {args.working_dir}"
    print("Scraping progress. Refer to 'crawl.log' for updates.")

    crawler = Crawler(
        site_map=None,
        working_dir=args.working_dir,
        snap=args.snap,
        langs=args.languages.split(),
    )

    crawler.scrape(
        save_interval=args.save_interval,
        rescrape=args.rescrape,
        allow_misalignments=args.allow_misalignments
    )

if args.crawl is False and args.scrape is False:
    raise RuntimeError("You must select an operation, either --crawl or --scrape.")
