# -*- coding: utf-8 -*-
import scrapy
import json
from usc.items import ReviewItem, ProfessorItem
import re

class RmpSpider(scrapy.Spider):
    name = 'rmp'
    allowed_domains = ['www.ratemyprofessors.com', 'solr-aws-elb-production.ratemyprofessors.com']
    
    start_urls = [
            'https://solr-aws-elb-production.ratemyprofessors.com//solr/rmp/select/?solrformat=true&rows=100&wt=json&json.wrf=noCB&callback=noCB&q=*%3A*+AND+schoolid_s%3A1381+AND+teacherdepartment_s%3A%22Engineering%22&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&bf=pow(total_number_of_ratings_i%2C2.1)&sort=total_number_of_ratings_i+desc&siteName=rmp&rows=20&start=0&fl=pk_id+teacherfirstname_t+teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&fq=',
            'https://solr-aws-elb-production.ratemyprofessors.com//solr/rmp/select/?solrformat=true&rows=60&wt=json&json.wrf=noCB&callback=noCB&q=*%3A*+AND+schoolid_s%3A1381+AND+teacherdepartment_s%3A%22Computer+Science%22&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&bf=pow(total_number_of_ratings_i%2C2.1)&sort=total_number_of_ratings_i+desc&siteName=rmp&rows=20&start=0&fl=pk_id+teacherfirstname_t+teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&fq=',
            'https://solr-aws-elb-production.ratemyprofessors.com//solr/rmp/select/?solrformat=true&rows=60&wt=json&json.wrf=noCB&callback=noCB&q=*%3A*+AND+schoolid_s%3A1106+AND+teacherdepartment_s%3A%22Engineering%22&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&bf=pow(total_number_of_ratings_i%2C2.1)&sort=total_number_of_ratings_i+desc&siteName=rmp&rows=20&start=0&fl=pk_id+teacherfirstname_t+teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&fq=',
            'https://solr-aws-elb-production.ratemyprofessors.com//solr/rmp/select/?solrformat=true&rows=40&wt=json&json.wrf=noCB&callback=noCB&q=*%3A*+AND+schoolid_s%3A1106+AND+teacherdepartment_s%3A%22Computer+Science%22&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&bf=pow(total_number_of_ratings_i%2C2.1)&sort=total_number_of_ratings_i+desc&siteName=rmp&rows=20&start=0&fl=pk_id+teacherfirstname_t+teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&fq=']
    """
     I found these request URLs by inspecting the RMP website in Google Chrome
     using the Network tab in the Dev Tools and modified it to get:
     100 USC Engineering profs, 60 USC CS profs, 60 UHM Engineering profs, 40 UHM CS profs
     They return a JSON object
    """
    
    #
    def parse(self, response):
        """
        This gets the Professor list and builds a Request url with the prof_id's,
        which will return a JSON of the pages of reviews
        """
        data = json.loads(response.text[5:-1])
        q = data['responseHeader']['params']['q']
        i1 = q.index('\"')
        department = q[i1+1:-1]
        profs = data['response']['docs']

        for prof in profs:
            item = ProfessorItem()
            item['department'] = department
            item['avg_rating'] = prof['averageratingscore_rf']
            item['prof_id'] = prof['pk_id']
            if prof['schoolid_s'] == '1381':
                item['school'] = 'USC'
            elif prof['schoolid_s'] == '1106':
                item['school'] = 'UHM'
                
            item['first_name'] = prof['teacherfirstname_t']
            item['last_name'] = prof['teacherlastname_t']
            item['full_name'] = item['first_name'] + ' ' + item['last_name']

            """
            This just generates a code based on the professor's first
            and last name. I was planning on using it somewhere.
            """
            if len(item['last_name']) < 4:
                item['last_name'] = item['last_name'] + 'ZZZ'
            item['name_code'] = item['first_name'][:2].upper() + item['last_name'][:4].upper()
            
            # TODO: Rewrite so that the in the response from this url, only continue to the next page if 'remaining' > 0
            urls = ['https://www.ratemyprofessors.com/paginate/professors/ratings?tid=' + str(item['prof_id']) + '&page=' + num for num in range(1,7) ]
            # This goes through 6 pages of reviews for each professor
            for url in urls:
                yield scrapy.Request(url=url,callback=self.parsePages, meta={'item':item}, dont_filter=True)

    def parsePages(self, response):
        """
        This gets the data from the JSON containing the reviews
        """
        data = json.loads(response.text)
        professor = response.request.meta["item"]
        if len(data['ratings']) > 0:
            item = ReviewItem()
            item['professor'] = professor
            for rating in data['ratings']:
                item = ReviewItem()
                item['professor'] = professor
                item['course_code'] = rating['rClass']
                if item['course_code'] != None and item['course_code'] != '':
                    index = re.search('\d', item['course_code']).start()
                    item['course_code'] = item['course_code'][:index] + '-' + item['course_code'][index:]
                item['full_course_code'] = item['professor']['school'] + '-' + item['course_code']
                item['review_id'] = rating['id']
                item['date'] = rating['rDate']
                item['overall_score'] = rating['rOverall']
                item['quality'] = rating['quality']
                item['comments'] = rating['rComments']
                item['tags'] = rating['teacherRatingTags']
                item['retake'] = rating['rWouldTakeAgain']
                item['online'] = rating['onlineClass']
                item['attendance'] = rating['attendance']
                item['difficulty'] = rating['rEasy']
                yield item
            
