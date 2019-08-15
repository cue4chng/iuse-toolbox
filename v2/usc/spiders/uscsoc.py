# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from usc.items import CourseItem
import re
from urllib.parse import urljoin



class UscsocSpider(scrapy.Spider):
    name = 'uscsoc'
    allowed_domains = ['web-app.usc.edu', 'web-app.usc', 'usc.edu']
    start_urls = ['https://web-app.usc.edu/ws/soc_archive/soc//']

    
    def parse(self, response): 
        """
        This starts at https://web-app.usc.edu/ws/soc_archive/soc/
        and selects each Term (example: Fall 2018)
        """
        sel = Selector(response)
        terms = sel.xpath('//*[@id="termdata"]//li/a/@href')
        # These selectors were found through trial and error.
        # http://xpather.com/ is a useful site
        terms = terms[2:13]
        for t in terms:
            item = CourseItem()
            url = 'https://web-app.usc.edu/ws/soc_archive/soc/' + t.get().strip()
            item['university'] = 'USC'
            item['term'] = t.get()[5:-1]
            item['code'] = 'USC'
            yield Request(url=url,callback=self.parseDepartments,meta={'item':item}, dont_filter=True)
    
    
    def parseDepartments(self, response): 
        """
        For each of the terms, it gets the list of
        departments inside the Viterbi School of Engineering
        """
        sel = Selector(response)
        departments = sel.xpath('//li[@data-school="Engineering" and @data-type="department"]/a')
        for d in departments:
            item = CourseItem(response.request.meta["item"])
            item['department'] = d.xpath('span/text()').get()
            href = d.xpath('@href').get().strip()
            url = urljoin('https://web-app.usc.edu', href)
            yield Request(url=url,callback=self.parseCourses,meta={'item':item}, dont_filter=True)
    
    def parseCourses(self, response):
        """
        For each of the departments, it gets the list of classes
        inside the department. (example: 101-794 in AME)
        """
        sel = Selector(response)
        courses = sel.xpath('//div[@class="course-info expandable"]')
        for c in courses:
            item = CourseItem(response.request.meta["item"])
            item['code'] += '-' + c.xpath('@id').get().strip()
            item['name'] = c.xpath('//a[@class="courselink"]/text()').get().strip()
            # everything works up to here #
            href = c.xpath('div/h3/a/@href').get()
            url = urljoin('https://web-app.usc.edu', href)
            yield Request(url=url,callback=self.parseSection,meta={'item':item})
    
    def parseSection(self, response):
        """
        For each of the classes, it gets the list of
        sections available. Each section has an
        instructor, syllabus, and section code
        """
        sel = Selector(response)
        sections = sel.xpath('//table[@class="sections responsive"]//tr[not(@class="headers")]')
        for s in sections:
            item = CourseItem(response.request.meta["item"])
            item['section'] = s.xpath('@data-section-id').get().strip()
            item['instructors'] = s.css('.instructor::text').get()
            if item['instructors'] != None:
                item['instructors'].strip()
                item['instructors'] = [x.strip() for x in re.split(',', item['instructors'])]
            item['syllabus'] = s.css('.syllabus a::attr(href)').get()
            if item['syllabus'] != None:
                item['syllabus'].strip()
            return item
        

        """
        Ignore the code below this. I was trying to get
        the times, days, and number registered from the class sections
        """
        #times = s.xpath('//td[@class="time"]/text()').get().strip()
        #times = re.split('-', times)
        #starttime = times[0]
        #endtime = times[1]
        #endt = dt.datetime.strptime(endtime, '%H:%M%p')
        # TODO: Check if "am"/"pm" from endt, & if endt hour is greater/less than startt 
        #startt = dt.datetime.strptime(starttime, '%H:%M')
        #days = s.xpath('//td[@class="days"]/text()').get().strip()
        #days = re.split(',', days)
        #numdays = len(days]
        
        #cap = s.xpath('//td[@class="registered"]//a/text()').get().strip()
        #cap = re.split(' of ', cap.strip())
        #item['capacity'] = cap[1]
    
