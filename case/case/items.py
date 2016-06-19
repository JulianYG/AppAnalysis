# -*- coding: utf-8 -*-

# Items: 
# --application_info: includes school and personal information
# 	of applicant 
# --pid: user id of applicant 
# --url: web address of current post 
# --reply: number of replies of current post
# --view: number of views of current post

import scrapy

class CaseItem(scrapy.Item):
	
	application_info = scrapy.Field()
	pid = scrapy.Field()
	url = scrapy.Field()
	reply = scrapy.Field()
	view = scrapy.Field()
