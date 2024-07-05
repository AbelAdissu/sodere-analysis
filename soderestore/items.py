import scrapy

class BookItem(scrapy.Item):
    full_link = scrapy.Field()
    title = scrapy.Field()
    image_path = scrapy.Field()
    shadow_text = scrapy.Field()
    price = scrapy.Field()
    additional_title = scrapy.Field()
    preprocessed_image_path = scrapy.Field()
