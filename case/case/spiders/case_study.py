# -*- coding: utf-8 -*-
import scrapy
from case.items import CaseItem
from scrapy.selector import Selector

class CaseStudySpider(scrapy.Spider):
	name = "caseStudy"
	allowed_domains = ["gter.net"]
	# Start from different regions
	start_urls = ["http://bbs.gter.net/thread-1985553-1-1.html", # UK & Europe
		"http://bbs.gter.net/thread-1988272-1-1.html", # US
		"http://bbs.gter.net/thread-1986767-1-1.html", # Canada
		"http://bbs.gter.net/thread-1982574-1-1.html", # HK & Macow & Taiwan
		"http://bbs.gter.net/thread-1986543-1-1.html", # Singapore
		"http://bbs.gter.net/thread-1812104-1-1.html", # Japan & S. Korea
		"http://bbs.gter.net/thread-1936839-1-1.html"] # Oceania

	def parse(self, response):
		category = response.xpath('(//*/h1[@class="ts"]/a/text())[1]').extract()[0]
		# only extract if this is offer post
		if category == '[Offer榜]':
			item = CaseItem()
			info = [n.encode('utf-8') for n in response.xpath('//div[@class="typeoption"]/table').extract()]	
			item['url'] = response.url
			item['application_info'] = info
			item['pid'] = (response.xpath('(//*/div[@class="authi"]/a/@href)[1]').extract()[0]\
				.split('-')[-1].split('.')[0]).encode('utf-8')
			item['reply'] = response.xpath('(//*/div[@class="hm"]/span[@class="xi1"]/text())[2]').extract()[0].encode('utf-8')
			item['view'] = response.xpath('(//*/div[@class="hm"]/span[@class="xi1"]/text())[1]').extract()[0].encode('utf-8')
			yield item

		for next_post in response.xpath('//div[@class="y"]'):
			href_lst = next_post.xpath('a/@href').extract()
			img_lst = next_post.xpath('a/img/@src').extract()
			for href, img in zip(href_lst, img_lst):
				if img.split('.')[0][-4:] == "prev":
					url = response.urljoin(href)
					yield scrapy.Request(url, callback = self.parse)
