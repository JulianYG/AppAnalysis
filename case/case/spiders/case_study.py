# -*- coding: utf-8 -*-
import scrapy
from case.items import CaseItem
from scrapy.selector import Selector
from bs4 import BeautifulSoup as BSoup

class CaseStudySpider(scrapy.Spider):
	name = "caseStudy"
	allowed_domains = ["gter.net"]
	# Start from different regions
	start_urls = [
		# UK
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=486&typeid=992&filter=typeid&typeid=992&page=", 
		# Europe
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=539&typeid=993&filter=typeid&typeid=993&page=", 
		# HK, Macow & Taiwan
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=811&typeid=994&filter=typeid&typeid=994&page=",
		# US
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=49&typeid=158&filter=typeid&typeid=158&page=", 
		# Canada
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=565&typeid=991&filter=typeid&typeid=991&page=", 
		# Singapore
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=812&typeid=995&filter=typeid&typeid=995&page=", 
		# Japan & S. Korea
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=484&typeid=996&filter=typeid&typeid=996&page=", 
		# Oceania
		"http://bbs.gter.net/forum.php?mod=forumdisplay&fid=128&typeid=997&filter=typeid&typeid=997&page="
		]

	def parse(self, response):
		"""
		Simply parse the offer list page to extract links to other pages
		"""
		suimono = BSoup(response.body, "lxml")
		page_urls = suimono.find_all("a", {"class": "last"})
		# Get the maximum number of pages in this region section
		if page_urls:
			max_page = int(page_urls[0].get_text().split(' ')[1])
		else:
			max_page = int(suimono.find("div", {"class": "pg"}).find_all('a')[-2].get_text())

		for i in range(1, max_page + 1):
			next_page = response.url[:-1] + str(i)
			yield scrapy.Request(next_page, callback = self.parse_post_on_page)

	def parse_post_on_page(self, response):
		"""
		Parse the list page source to extract links to actual posts
		"""
		tonkotsu = BSoup(response.body, "lxml")
		post_urls = tonkotsu.find_all("a", {"class": "xst"}, href=True)
		

		for post in post_urls:
			thread_link = post['href']
			yield scrapy.Request(thread_link, callback=self.parse_post)
		

	def parse_post(self, response):
		"""
		Parse the actual content inside each post
		"""
		category = response.xpath('(//*/h1[@class="ts"]/a/text())[1]').extract()[0]
		# only extract if this is offer post
		if category == '[Offer榜]':
			info = [n.encode('utf-8') for n in response.xpath('//div[@class="typeoption"]/table').extract()]	
			if len(info) > 1:
				item = CaseItem()
				item['region'] = self.parse_region(response.xpath('//title/text()').extract()[0])
				item['application_info'] = info 
				item['url'] = response.url
				item['pid'] = (response.xpath('(//*/div[@class="authi"]/a/@href)[1]').extract()[0]\
					.split('-')[-1].split('.')[0]).encode('utf-8')
				item['reply'] = response.xpath('(//*/div[@class="hm"]/span[@class="xi1"]/text())[2]').extract()[0].encode('utf-8')
				item['view'] = response.xpath('(//*/div[@class="hm"]/span[@class="xi1"]/text())[1]').extract()[0].encode('utf-8')
				yield item

	def parse_region(self, title_str):
		"""
		Parse the name of application region
		"""
		region = ' '.join((title_str.strip().split())).split(' ')[-2]
		region_str = ''
		if region == '日韩留学':
			region_str = 'JP/SK'
		if region == '新加坡留学':
			region_str = 'Singapore'
		if region == '加拿大留学申请':
			region_str = 'Canada'
		if region == '欧洲诸国留学':
			region_str = 'Europe'
		if region == '澳洲新西兰留学与移民':
			region_str = 'Oceania'
		if region == '美国留学':
			region_str = 'US'
		if region == '英国留学申请':
			region_str = 'UK'
		if region == '香港澳门台湾留学':
			region_str = 'HK/MO/TW'
		return region_str

