# JW Crawler
_Debido a la intransigencia de los Testigos de Jehová, nos vemos obligados a implementar [nuestro propio](https://gitlab.com/Feasinde/jw_crawler) *crawler* para extraer los invaluables *corpora* paralelos de [JW.org](https://www.jw.org/es/)._

`jw_crawler.py` is a webcrawler using [Selenium](https://www.selenium.dev/) and Firefox via the [geckodriver](https://github.com/mozilla/geckodriver) that retrieves parallel text from the official Jehova's Witnesses' website, [jw.org](https://www.jw.org).

The crawling strategy is simple: download a sitemap file and use it to visit all available URLs, specifying which languages to look for.

## Installation
Simply clone the repo and install the requirements. The easiest way of doing so is to create a virtual environment in Python 3.9 and running `pip install -r requirements.txt`.

## Overview
Each URL is treated as a potential source of parallel texts. Whenever a visited URL contains the option of reading any of the Mayan languages, it is stored as a `ParallelDocument` object, containing the URL and the languages it contains.

Once the crawl begins, a dictionary of URLs where the key is the URL and the value is whether it has been visited yet or not. 

## Usage
Run the crawler with `python jw_crawl.py` followed by the required and optional arguments. 
```
Crawl the website jw.org for parallel corpora

optional arguments:
  -h, --help            show this help message and exit
  -c, --crawl           Runs crawl operation, which gathers parallel documents
                        from JW.org
  -s, --scrape          Runs scrape operation, which extractsparallel text
                        from parallel documentsand saves them as dataframes
  --scrape_docs, -S     Scrape parallel documents found in
                        'parallel_documents.json' file inworking directory.
  --working_dir WORKING_DIR
                        Sets working directory. Default: main language
  --rescrape, -R        Rescrape all parallel documents on disk
  --main_language MAIN_LANGUAGE
                        Sets language for downloading the site map.
  --languages LANGUAGES
                        Sets languages to look for during crawl and scrape
  -p, --load_parallel_docs
                        Loads saved list of parallel docs.
  -v, --load_visited_urls
                        Loads saved list of visited urls
  --save_interval SAVE_INTERVAL
                        Sets how often to save parallel docs
  --max_number_parallel_docs MAX_NUMBER_PARALLEL_DOCS
                        Sets max number of parallel docs to gather
  --exclude EXCLUDE     String containing tokens to exclude from site map
                        separated by spaces. Default: None
  --snap, -n            Include if using the Snap version of Firefox
  --no_misalignments, -m
                        Gather dataframes from paralleldocuments whose
                        paragraphs do not align exactly across languages.
                        Reduces precision of parallel texts. Default: False
  --create_ospl, -o     Create parallel corpora following the'One Sentence Per
                        Line' format. Default: False

Inspired by the tireless efforts of the JW300 team
```

## Examples of use

Crawl and scrape the Spanish version of the website looking for the Mayan languages k'iche', mam, and tzeltal:
```bash
$ python jw_crawler.py --crawl --scrape --main_language es --languages "quc mam tzh"
``` 

Same as above, excluding the New World Translation Bible and the terms of use:
```bash
$ python jw_crawler.py --crawl --scrape --main_language es --languages "quc mam tzh" --exclude "biblia/nwt/libros condiciones-de-uso"
``` 

Reload an interrupted crawl session:
```bash
$ python jw_crawler.py --crawl --load_parallel_docs --load_visited_urls --main_language es --languages "quc mam tzh"
```

Scrape a list of URLs specified in the `es/parallel_documents.json` file.
```bash
$ python jw_crawler.py --scrape_docs --working_dir es
```

Create parallel text files for Spanish following the One Sentence Per Line format:
```bash
$ python $jw_crawler.py --create_ospl --main_language es
```

Same as above for only for target languages Mam and Yucatec Mayan:
```bash
$ python $jw_crawler.py --create_ospl --main_language es --languages "mam yua"
```