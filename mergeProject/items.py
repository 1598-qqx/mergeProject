# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MergeprojectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    b_name = scrapy.Field()
    b_author = scrapy.Field()
    b_type = scrapy.Field()
    b_intro = scrapy.Field()
