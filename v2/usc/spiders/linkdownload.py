# -*- coding: utf-8 -*-
import scrapy
import json

urls = []
with open('syllabuslinks.json') as file:
    links = json.load(file)
    urls = links


class LinkdownloadSpider(scrapy.Spider):
    """
    This downloads the syllabus files (pdf/doc)
    from thelist of links inside "syllabuslinks.json"
    and puts the class code as the file name.
    """
    name = 'linkdownload'
    allowed_domains = ['https://web-app.usc.edu/']
    start_urls = ['https://web-app.usc.edu//']

    def parse(self, response):
        for u in urls:
            yield scrapy.Request(url=u['url'],callback=self.parseFile, meta={'name':u['name']}, dont_filter=True)

    def parseFile(self, response):
        ext = response.request.url[-4:]
        path = response.request.meta['name'] + ext
        with open(path, "wb") as f:
            f.write(response.body)
