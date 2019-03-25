### Syllabus Scraper

Build and run through Docker. Clone the repo, `cd` into the project folder, and run
```
docker build --tag auto-miner .
docker run docker run -v /$(pwd):/app auto-miner python -m scraper [options]
```
# Note: `auto-miner` is a provisional name only(!)

**Options**
 `--seed_url`
 Specify a single seed URL
`--seed_url_file` 
Seed URLs will be read from a file
`--output_path`
Specify directory to write crawl data to. Data will be saved in a single file `output.{csv|json}`.
`--pagecount`
Max pages to fetch
`--max_depth`
Max depth of links to follow.
`--format`
Crawl data format, one of `json` or `csv`

**Sample run**

To run a crawler on [USC's CS courses page](https://www.cs.usc.edu/academic-programs/courses/) to crawl ten web pages and write to the directory `crawl_data/`, run
```
docker run -v /$(pwd):/app auto-miner python -m scraper \
	--seed_url https://www.cs.usc.edu/academic-programs/courses/ \
	--data_dir crawl_data/ \
	--pagecount 10 \
	--max_depth 3 \
	--format csv


```

Output:

```
$ more crawl_data/output.json -n 1  
[{"url": "https://www.cs.usc.edu/academic-programs/courses/", "body": "...", ...}]
```

Logging:

```
Visited https://www.cs.usc.edu/academic-programs/courses/
Visited https://www.cs.usc.edu/academic-programs/phd/
Visited https://www.cs.usc.edu/academic-programs/
Visited https://www.cs.usc.edu/academic-programs/courses/
Visited https://www.cs.usc.edu/research/annual-research-review/
Visited https://www.cs.usc.edu/students/cs-job-announcements/
Visited https://www.cs.usc.edu/academic-programs/graduate-certificate/
Visited https://www.cs.usc.edu/special-topics-courses/
Visited https://www.cs.usc.edu/people/staff-directory/
Visited https://www.cs.usc.edu/about/bekey-lecture/
Visited https://www.cs.usc.edu/academic-programs/phd/old-program/
Visited https://www.cs.usc.edu/about/newsletters/
Visited https://www.cs.usc.edu/news/
Visited https://www.cs.usc.edu/students/cs-student-organizations/
```
