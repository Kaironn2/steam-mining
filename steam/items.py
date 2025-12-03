# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Achievement(scrapy.Item):
    username = scrapy.Field()
    game = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    unlock_time = scrapy.Field()
    unlocked = scrapy.Field()
    total = scrapy.Field()
    current_progress = scrapy.Field()
    total_progress = scrapy.Field()
    language = scrapy.Field()
    url = scrapy.Field()
