"""Sample run: 

python3 -m scraper \
    --seed_url https://classes.usc.edu/term-20191/classes/csci/ \
    --allowed_domains usc.edu \
    --output_path crawl_data/ \
    --pagecount 100 \
    --max_depth 5 \
    --format csv
"""
from . import scraper
import argparse
from urllib.parse import urlparse
import re
import os
import tldextract

# Django regex for URL validation (https://stackoverflow.com/a/7160778)
regex = re.compile(
  r'^(?:http|ftp)s?://'  # http:// or https://
  # domain...
  r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
  r'localhost|'  # localhost...
  r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
  r'(?::\d+)?'  # optional port
  r'(?:/?|[/?]\S+)$', re.IGNORECASE)


def validate_url(url):
  if not regex.match(url):
    raise argparse.ArgumentTypeError('Boolean value expected.')

  return url


def get_domain(url):
  uri = tldextract.extract(url)
  return f'{uri.domain}.{uri.suffix}'


parser = argparse.ArgumentParser(description='IUSE Toolbox: Scraper Utility')
parser.add_argument(
  '--output_path',
  required=False,
  default=os.path.join(os.getcwd(), 'data'),
  help='Directory to write scraped data to.')

parser.add_argument(
  '--seed_url',
  required=False,
  type=validate_url,
  help='Seed URL for the crawler. Only one URL can be specified.')

parser.add_argument(
  '--seed_url_file',
  required=False,
  help='Import seed URLs from a file.')

parser.add_argument(
  '--allowed_domains',
  required=False,
  type=str,
  nargs='+',
  default=[],
  help='Additional allowed domains (usage: --allowed_domains a b c).')

parser.add_argument(
  '--pagecount',
  required=False,
  type=int,
  default=100,
  help='Maximum number of pages to fetch.')

parser.add_argument(
  '--max_depth',
  required=False,
  type=int,
  default=5,
  help='Maximum links to follow from start_url.')


parser.add_argument(
  '--format',
  required=False,
  choices=['csv', 'json'],
  default='csv',
  help='Output format. Currently only supports CSV or JSON.')


args = vars(parser.parse_args())

if not (args['seed_url'] or args['seed_url_file']):
  raise argparse.ArgumentTypeError(
    'One of start_url or seed_url_file must be specified.')

if args['seed_url']:
  seeds = [args['seed_url']]
else:
  seeds = open(args['seed_url_file']).read().splitlines()

allowed_domains = sorted(set([get_domain(u)
                for u in seeds] + args['allowed_domains']))

crawler_cls = scraper.init_spider(allowed_domains=allowed_domains,
                  start_urls=seeds, )

crawl_settings = {
  # Can be changed later as needed.'
  'CLOSESPIDER_PAGECOUNT': args['pagecount'],
  'DEPTH_LIMIT': args['max_depth']
}

scraper.run_spider(crawler_cls, **crawl_settings,
           data_dir=args['output_path'], feed_format=args['format'])
