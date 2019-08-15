# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CourseItem(scrapy.Item):
    #Terms Page
    university = scrapy.Field()
    term = scrapy.Field() #e.g. 20191
        # spring = 1, summer = 2, fall = 3
    #Departments Page
    department = scrapy.Field() #e.g. CSCI

    #Courses Page
    name = scrapy.Field()
    code = scrapy.Field()

    #Sections Page
    section = scrapy.Field()
    #times = scrapy.Field()
    #days = scrapy.Field()
    #classtime = scrapy.Field()
    #capacity = scrapy.Field() 
    instructors = scrapy.Field() #list str. multiple profs split with ,
    syllabus = scrapy.Field() 


class ReviewItem(scrapy.Item):
    professor = scrapy.Field() #ProfessorItem
    course_code = scrapy.Field() 
    full_course_code = scrapy.Field()
    review_id = scrapy.Field() 
    date = scrapy.Field() 
    overall_score = scrapy.Field() 
    quality = scrapy.Field() 
    comments = scrapy.Field() 
    tags = scrapy.Field() 
    retake = scrapy.Field() 
    online = scrapy.Field() 
    attendance =  scrapy.Field() 
    difficulty = scrapy.Field()

class ProfessorItem(scrapy.Item):
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    full_name = scrapy.Field()
    name_code = scrapy.Field() 
    school = scrapy.Field() #USC sid = 1381. UHM sid = 1106
    department = scrapy.Field() 
    avg_rating = scrapy.Field() 
    prof_id = scrapy.Field()

