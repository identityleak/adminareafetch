# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StatespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class ProvinceItem(scrapy.Item):
    collection_name = 'Province'
    code = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    cities = scrapy.Field()

class CityItem(scrapy.Item):
    collection_name = 'City'
    name = scrapy.Field()
    code = scrapy.Field()
    link = scrapy.Field()
    towns = scrapy.Field()

class TownItem(scrapy.Item):
    collection_name = 'Town'
    name = scrapy.Field()
    code = scrapy.Field()
    link = scrapy.Field()
    villages = scrapy.Field()

class VillageItem(scrapy.Item):
    collection_name = 'Village'
    name = scrapy.Field()
    code = scrapy.Field()
    catalog = scrapy.Field()
