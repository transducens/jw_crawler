import argparse
import json
import os
import shutil

from src.crawler import Crawler
from src.sitemap import SiteMap
from src.ospl import OneSentencePerLine


def check_for_existing_file_or_dir(name: str) -> None:
    delete_file = input(f"'{name}' exists and would be overwritten. "
                        f"Continue? (y/n)")
    while ((delete_file == "y") or (delete_file == "n")) is False:
        delete_file = input("Please enter 'y' or 'n'")

    if delete_file == "y":
        if os.path.isdir(name):
            shutil.rmtree(name)
        else:
            os.remove(f"{name}")
    else:
        exit(0)


parser = argparse.ArgumentParser(
    prog="jw_crawler",
    description="Crawl the website jw.org for parallel corpora",
    epilog="Inspired by the tireless efforts of the JW300 team"
)

parser.add_argument("-c", "--crawl", action='store_true', default=False, help="Runs crawl operation, which gathers "
                                                                              "parallel documents from JW.org")
parser.add_argument("-s", "--scrape", action='store_true', default=False, help="Runs scrape operation, which extracts"
                                                                               "parallel text from parallel documents"
                                                                               "and saves them as dataframes")
parser.add_argument("--scrape_docs", "-S", action='store_true', default=False, help="Scrape parallel documents found in "
                                                                              "'parallel_documents.json' file in"
                                                                              "working directory.")
parser.add_argument("--working_dir", help="Sets working directory. Default: main language", default=""),
parser.add_argument("--rescrape", "-R", action='store_true', default=False, help="Rescrape all parallel documents on disk")
parser.add_argument("--main_language", help="Sets language for downloading the site map.")
parser.add_argument("--languages", help="Sets languages to look for during crawl and scrape")
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
parser.add_argument("--snap", "-n", action='store_true', default=False, help="Include if using the Snap version of Firefox")
parser.add_argument("--no_misalignments", "-m", action='store_true', default=False, help="Gather dataframes from parallel"
                                                                                      "documents whose paragraphs do "
                                                                                      "not align exactly across "
                                                                                      "languages. Reduces precision of "
                                                                                      "parallel texts. Default: False")
parser.add_argument("--create_ospl", "-o", action='store_true', default=False, help="Create parallel corpora following the"
                                                                              "'One Sentence Per Line' format. Default"
                                                                              ": False")

args = parser.parse_args()
if args.working_dir == "":
    args.working_dir = args.main_language

if args.crawl is True:

    assert args.main_language is not None, f"No main language specified. Use --main_language followed by the ISO " \
                                           f"language code"

    assert args.languages is not None, f"No list of languages specified. Use blank-separated string of ISO language " \
                                       f"codes"

    if os.path.exists(args.working_dir) is False:
        os.mkdir(args.working_dir)

    if args.scrape is True:
        if os.path.exists(f"{args.working_dir}/dataframes"):
            check_for_existing_file_or_dir(f"{args.working_dir}/dataframes")
        os.mkdir(f"{args.working_dir}/dataframes")

    if args.load_visited_urls is False:
        if os.path.exists(f"{args.working_dir}/visited_urls.json"):
            check_for_existing_file_or_dir(f"{args.working_dir}/visited_urls.json")
    else:
        try:
            with open(f"{args.working_dir}/visited_urls.json") as f:
                visited_urls = json.loads(f.read())
        except FileNotFoundError as e:
            print(f"{e}. No 'visited_urls.json' file found in working dir. Use --site_map_url to fetch a new site map.")
            exit(1)

    if args.load_parallel_docs is False:
        if os.path.exists(f"{args.working_dir}/parallel_documents.json"):
            check_for_existing_file_or_dir(f"{args.working_dir}/parallel_documents.json")
    else:
        assert os.path.exists(f"{args.working_dir}/parallel_documents.json"), f"No 'parallel_documents.json' file " \
                                                                              f"found."

    if os.path.exists(args.working_dir) is False:
        os.mkdir(args.working_dir)

    print("Crawling in progress. Refer to 'crawl.log' for updates.")
    
    crawler = Crawler(
        site_map=SiteMap(
            main_language=args.main_language,
            exclude=args.exclude.split(" ") if args.exclude is not None else None,
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
        scrape=args.scrape,
        no_misalignments=args.no_misalignments
    )

if args.scrape_docs:
    assert args.working_dir is not None, "No working directory specified"
    assert os.path.exists(f"{args.working_dir}/parallel_documents.json"), f"'parallel_documents.json' not found in " \
                                                                          f"working directory {args.working_dir}"
    with open(f"{args.working_dir}/parallel_documents.json") as f:
        scraped_docs = json.loads(f.read())
        scraped_docs = [scraped_docs[key]['is_scraped'] for key in scraped_docs.keys() if "time" not in key]
        assert False in scraped_docs, "No unscraped parallel docs in 'parallel_documents.json'"

    if os.path.exists(f"{args.working_dir}/dataframes"):
        check_for_existing_file_or_dir(f"{args.working_dir}/dataframes")
    os.mkdir(f"{args.working_dir}/dataframes")

    print("Scraping progress. Refer to 'crawl.log' for updates.")

    crawler = Crawler(
        site_map=None,
        working_dir=args.working_dir,
        snap=args.snap,
        langs=args.languages.split() if args.languages is not None else None,
    )

    crawler.scrape(
        save_interval=args.save_interval,
        rescrape=args.rescrape,
        no_misalignments=args.no_misalignments
    )

if args.create_ospl:
    assert args.main_language is not None, f"No main language specified. Use --main_language followed by "\
                                           f"the ISO language code."
    assert os.path.exists(f"{args.working_dir}/dataframes"), f"No 'dataframes' folder in working directory " \
                                                             f"'{args.working_dir}'"
    assert os.listdir(f"{args.working_dir}/dataframes") != [], f"'dataframes' folder in working directory " \
                                                               f"{args.working_dir} is empty."

    ospl = OneSentencePerLine(working_dir=args.working_dir,
                              langs=args.languages.split() if args.languages is not None else None,
                              main_lang=args.main_language
                              )
    ospl.create_ospl()

if args.crawl is False and args.scrape_docs is False and args.create_ospl is False:
    raise RuntimeError("You must select an operation, either --crawl, --scrape, or --create_ospl.")
