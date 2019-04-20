## Syllabus Scraper

Build and run through Docker. Clone the repo, `cd` into the project folder, and run
```
docker build --tag auto-miner .
docker run -v /$(pwd):/app auto-miner python -m scraper [options]
```
(Note: `auto-miner` is a provisional name only(!))

**Options**
- `--output_path` (REQUIRED): Specify directory to write crawl data to. 
- `--seed_url`: Specify a single seed URL
- `--seed_url_file`: Seed URLs will be read from a file
- `--pagecount`: Max pages to fetch
- `--max_depth`: Max depth of links to follow.
- `--format`: Crawl data format, one of `json` or `csv`

Note: One of `--seed_url` or `--seed_url_file` must be specified to run the crawler.

**Sample run**

To run a crawler on [USC's CS Spring19 Courses page](https://classes.usc.edu/term-20191/classes/csci/) and write to the directory `crawl_data/`, run
```
docker run -v /$(pwd):/app auto-miner python -m scraper \
    --seed_url https://classes.usc.edu/term-20191/classes/csci/ \
    --allowed_domains usc.edu \
    --output_path crawl_data/ \
    --pagecount 100 \
    --max_depth 5 \
    --format csv
```

Relevant pages are determined using a set of keywords. These pages are then scraped and written to `crawl_data/`. A mapping file of {url: filpath} is also created as `mapping.{json|csv}`.
