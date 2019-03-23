from twisted.internet import reactor

import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.conf import settings
from scrapy.utils.project import get_project_settings

from multiprocessing import Process, Queue

SETTINGS = get_project_settings()


# TODO - implement persisting scraped data to disk.
def init_spider(**kwargs):
    class Spider(scrapy.Spider):
        name = "edu_scraper"
        allowed_domains = kwargs.pop('allowed_domains', [])
        start_urls = kwargs.pop('start_urls', [])
        data_dir = kwargs.pop('data_dir', None)
            
        def parse(self, response):
            print(f'Visited {response.url}')
            
            for href in response.xpath('//a/@href').getall():
                yield scrapy.Request(response.urljoin(href), self.parse)
        
            yield response 
        
        def closed(self, reason):
            print(f'{spider.name} closed.')
            
    return Spider

# Modified from https://stackoverflow.com/a/43661172/4909087
def run_spider(spider, **kwargs):
    settings = SETTINGS.copy()
    settings.update(kwargs)
    
    def f(q):
        try:
            runner = CrawlerRunner(settings)
            deferred = runner.crawl(spider)
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