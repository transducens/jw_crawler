# JW Crawler
_Debido a la intransigencia de los Testigos de Jehová, nos vemos obligados a implementar [nuestro propio](https://gitlab.com/Feasinde/jw_crawler) *crawler* para extraer los invaluables *corpora* paralelos de [JW.org](https://www.jw.org/es/)._

`jw_crawler.py` is a webcrawler using [Selenium](https://www.selenium.dev/) and Firefox via the [geckodriver](https://github.com/mozilla/geckodriver).

The current strategy, which may be refined later on, is to use the [`sitemap.xml`](https://www.jw.org/es/sitemap.xml) file of the Spanish version of the website to visit all URLs and try and see if there are Mayan language versions of these focusing on the ten languages of our interest (cak, kek, mam, kjb, ctu, quc, poh, tzh, tzo, yua).


## Installation
Simply clone the repo and install the requirements. The easiest way of doing so is to create a virtual environment in Python 3.9 and running `pip install -r requirements.txt`.

## Overview
Each URL is treated as a potential source of parallel texts. Whenever a visited URL contains the option of reading any of the Mayan languages, it is stored as a `ParallelDocument` object, containing the URL and the languages it contains.

Once the crawl begins, a dictionary of URLs where the key is the URL and the value is whether it has been visited yet or not. 

## Usage
Run the crawler with `python jw_crawl.py` followed by the required and optional arguments. 
```
Crawl the website jw.org for Mayan languages

optional arguments:
  -h, --help            show this help message and exit
  -c, --crawl           Runs crawl operation, which gathers parallel documents from JW.org
  -s, --scrape          Runs scrape operation, which extractsparallel text from parallel documentsand saves them as dataframes
  --site_map_url SITE_MAP_URL
                        Sets URL of site map to be downloaded before beginningcrawl operation
  --working_dir WORKING_DIR
                        Sets working directory. Default is the same directory as script
  --load_parallel_docs  Loads saved list of parallel docs.
  --load_visited_urls   Loads saved list of visited urls
  --parallel_docs_save_interval PARALLEL_DOCS_SAVE_INTERVAL
                        Sets how often to save parallel docs
  --parallel_texts_save_interval PARALLEL_TEXTS_SAVE_INTERVAL
                        Sets how often to save parallel docs after being scraped
  --max_number_parallel_docs MAX_NUMBER_PARALLEL_DOCS
                        Sets max number of parallel docs to gather
  --exclude EXCLUDE     Pass a string containing tokens to exclude from site map separated by spaces
  --snap                Include if using the Snap version of Firefox

Inspired by the tireless efforts of the JW300 team

```
## Por hacer
- [x] Incluir un listado de strings que deban ser excluidos de los URLs recopilados
- [ ] ~~Incluir un listado de strings en los que haya que enfocarse para reducir el número de URLs recopilados, eg `"noticias"`, para que el *crawler* se enfoque en noticias~~
- [x] Codificar una CLI
- [x] Elucidar la estructura en común que tienen las páginas en múltiples idiomas.
	- Actualmente, parece ser que las etiquetas de la forma  `<p id='px'>` corresponden a textos paralelos.  
- [x] Funcionalidad para pausar y retomar el *crawling* una vez comenzado.
	- Guardar el progreso cada cierto tiempo o cada cierto número de documentos procesados.