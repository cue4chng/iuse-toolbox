from twisted.internet import reactor

import os
import scrapy

from scrapy import signals
from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.conf import settings
from scrapy.utils.project import get_project_settings

from multiprocessing import Process, Queue
from pathlib import Path

SETTINGS = get_project_settings()


class Item(scrapy.Item):
    url = scrapy.Field()
    body = scrapy.Field()
    

def init_spider(**kwargs):
    class Spider(scrapy.Spider):
        name = "edu_scraper"
        allowed_domains = kwargs.pop('allowed_domains', [])
        start_urls = kwargs.pop('start_urls', [])

        def parse(self, response):  
            print(f'Visited {response.url}') 
            item = Item()
            item['url'] = response.url
            item['body'] = response.body_as_unicode()
            yield item
                
            for href in set(response.xpath('//a/@href').getall()):
                yield scrapy.Request(response.urljoin(href), self.parse)

            yield response 
        
        def closed(self, reason):
            print(f'{spider.name} closed.')
            
    return Spider

# Modified from https://stackoverflow.com/a/43661172/4909087
def run_spider(spider, **kwargs):
    settings = get_project_settings()

    data_dir = kwargs.pop('data_dir', None)
    if data_dir:
        if not os.path.exists(data_dir):
            os.makedirs(Path(data_dir).absolute())
            
        feed_format = kwargs.pop('feed_format')
        settings.update({
            'FEED_FORMAT': feed_format,
            'FEED_URI': os.path.join(data_dir, 'output.' + feed_format)
        })
    settings.update(kwargs)
    
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