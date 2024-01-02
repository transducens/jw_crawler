# JW Crawler

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
  -c, --crawl           Runs crawl operation, which gathers parallel documents from JW.org
  -s, --scrape          Runs scrape operation, which extracts parallel text from parallel documentsand saves them as dataframes
  --scrape-docs, -S     Scrape parallel documents found in 'parallel_documents.json' file inworking directory.
  --working-dir WORKING_DIR
                        Sets working directory. Default: main language
  --rescrape, -R        Rescrape all parallel documents on disk
  --main-language MAIN_LANGUAGE
                        Sets language for downloading the site map. Default: en
  --languages LANGUAGES
                        Sets languages to look for during crawl and scrape
  -p, --load-parallel-docs
                        Loads saved list of parallel docs.
  -v, --load-visited-urls
                        Loads saved list of visited urls
  --save-interval SAVE_INTERVAL
                        Sets how often to save parallel docs
  -n MAX_NUMBER_PARALLEL_DOCS, --max-number-parallel-docs MAX_NUMBER_PARALLEL_DOCS
                        Sets max number of parallel docs to gather
  --exclude EXCLUDE     String containing tokens to exclude from site map separated by spaces. Default: None
  --snap                Include if using the Snap version of Firefox
  --allow-misalignments, -m
                        Gather dataframes from paralleldocuments whose paragraphs do not align exactly across languages. Reduces precision of parallel texts. Default: False
  --create-ospl, -o     Experimental. Create parallel corpora following the'One Sentence Per Line' format. Default: False


Inspired by the tireless efforts of the JW300 team
```

## Examples of use

Crawl and scrape the website for French and German documents using the default English-language site map
```bash
$ python jw_crawler.py --crawl --scrape --languages "fr de"
```
alternatively
```bash
$ python jw_crawler.py -cs --languages "fr de"
```

Crawl and scrape the Spanish version of the website looking for the Mayan languages k'iche', mam, and tzeltal:
```bash
$ python jw_crawler.py -cs --main-language es --languages "quc mam tzh"
``` 

Same as above, excluding the New World Translation Bible and the terms of use:
```bash
$ python jw-crawler.py -cs --main-language es --languages "quc mam tzh" --exclude "biblia/nwt/libros condiciones-de-uso"
``` 

Reload an interrupted crawl session:
```bash
$ python jw-crawler.py --crawl --load-parallel-docs --load-visited-urls --main-language es --languages "quc mam tzh"
```

Scrape a list of URLs specified in the `es/parallel_documents.json` file.
```bash
$ python jw_crawler.py --scrape-docs --working-dir es
```

Create parallel text files for Spanish following the One Sentence Per Line format:
```bash
$ python $jw_crawler.py --create-ospl --main-language es
```

Same as above for only for target languages Mam and Yucatec Mayan:
```bash
$ python $jw_crawler.py --create-ospl --main-language es --languages "mam yua"
```
