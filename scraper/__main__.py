from . import scraper
import argparse 
from urllib.parse import urlparse
import re
import os

# Django regex for URL validation (https://stackoverflow.com/a/7160778)
regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def validate_url(url):
    if not regex.match(url): 
    	raise argparse.ArgumentTypeError('Boolean value expected.')

    return url

parser = argparse.ArgumentParser(description='IUSE Toolbox: Scraper Utility')
parser.add_argument(
	  			  '--start_url', 
                  required=True, 
                  type=validate_url,
                  help='Seed URL for the crawler.')

# parser.add_argument(
# 	  			  '--output_path', 
#                   required=False,
#                   default=os.path.join(os.getcwd(), 'data'), 
#                   help='Output path for crawled data.')

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
                  default=10,
                  help='Maximum number of pages to fetch.')

parser.add_argument(
	  			  '--max_depth', 
                  required=False, 
                  type=int, 
                  default=5,
                  help='Maximum links to follow from start_url.')


args = vars(parser.parse_args())
seed = args['start_url']

allowed_domains = [urlparse(seed).netloc, *args['allowed_domains']]

crawler_cls = scraper.init_spider(allowed_domains=allowed_domains, 
                      		      start_urls=[seed], )

crawl_settings = {
  'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
  'CLOSESPIDER_PAGECOUNT': args['pagecount'],  # Can be changed later as needed.'
  'DEPTH_LIMIT': args['max_depth']
}

scraper.run_spider(crawler_cls, **crawl_settings)