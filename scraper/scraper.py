from twisted.internet import reactor

import os
import scrapy
import uuid

from scrapy import signals
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

from multiprocessing import Process, Queue
from pathlib import Path
from urllib.parse import urlparse

# Hardcoded for now, can be extended/loaded from file.
keywords = ['syllabus', 'curricul', 'lecture', ]
# extend to support video formats...
binary = {'pdf', 'doc', 'docx', 'ppt', 'pptx'}
allowed_extensions = {f'.{e}' for e in binary} | {'.html', ''}


class Item(scrapy.Item):
  url = scrapy.Field()
  mimetype = scrapy.Field()
  path = scrapy.Field()


class CustomLinkExtractor(LinkExtractor):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # Keep the default values in "deny_extensions" *except* for those types we want.
    self.deny_extensions = [
      ext for ext in self.deny_extensions if ext not in allowed_extensions]


def init_spider(**kwargs):
  class Spider(scrapy.Spider):
    name = 'edu_scraper'
    allowed_domains = kwargs.pop('allowed_domains')
    start_urls = kwargs.pop('start_urls')

    custom_settings = {
      'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    }

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
      """Entry point to the crawler program.

      Set `data_dir` before crawling. This is the only way to
      access overwritten/custom settings directly.
      """
      spider = super(Spider, cls).from_crawler(crawler, *args, **kwargs)
      spider.data_dir = crawler.settings.get('DATA_DIR')

      return spider

    def __init__(self, *args, **kwargs):
      self.rules = (Rule(CustomLinkExtractor(),
                 follow=True, callback='parse'),)
      super().__init__(*args, **kwargs)

    def parse(self, response):
      url = response.url.lower()

      # A better way to do this would be to observe `response.headers['Content-Type']`
      # and decide whether the mimetype is allowed.
      ext = os.path.splitext(urlparse(url).path)[1]

      if ext in allowed_extensions and any(k in url for k in keywords):
        # The else part is just a guess for now.
        ext = ext.lstrip('.') if ext else 'html'  

        # Write scraped content to `data_dir`.
        filedir = os.path.join(self.data_dir, ext)
        if not os.path.exists(filedir):
          os.makedirs(filedir)

        filepath = os.path.join(filedir, f'{str(uuid.uuid4())}.{ext}')
        with open(filepath, 'wb' if ext in binary else 'w') as f:
          f.write(
            response.body if ext in binary else response.body_as_unicode())

        # Write {url: path} mapping to the mapping.csv (or .json) file.
        item = Item()
        item['url'] = url
        item['mimetype'] = response.headers['Content-Type'].decode().split(';')[0]
        item['path'] = str(Path(filepath).absolute())

        yield item

      if hasattr(response, 'text'):
        # Page is text/html. Follow its links.
        for href in set(response.xpath('//a/@href').getall()):
          yield scrapy.Request(response.urljoin(href), self.parse)

  return Spider


# Modified from https://stackoverflow.com/a/43661172/4909087
def run_spider(spider, data_dir, **kwargs):
  feed_format = kwargs.pop('feed_format', 'csv')

  if not os.path.exists(data_dir):
    os.makedirs(Path(data_dir).absolute())

  # Create a copy of the settings and override with user arguments.
  settings = get_project_settings().copy()
  settings.update({
    'DATA_DIR': data_dir,
    'FEED_FORMAT': feed_format,
    'FEED_URI': os.path.join(data_dir, 'mapping.' + feed_format),
    **kwargs
  })

  def f(q):
    try:
      c = CrawlerProcess(settings)
      deferred = c.crawl(spider)
      deferred.addBoth(lambda _: reactor.stop())
      reactor.run()
      q.put(None)
    except Exception as e:
      q.put(e)

  q = Queue()
  p = Process(target=f, args=(q,))
  p.start()
  result = q.get()
  p.join()

  if result is not None:
    raise result
