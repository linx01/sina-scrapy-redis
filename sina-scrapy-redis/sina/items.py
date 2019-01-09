# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaItem(scrapy.Item):
	preTitle = scrapy.Field()
	preUrl = scrapy.Field() 
	subTitle = scrapy.Field()
	subUrl = scrapy.Field()
	subFilepath = scrapy.Field()
	textUrl = scrapy.Field()
	textHead = scrapy.Field()
	textContent = scrapy.Field()
