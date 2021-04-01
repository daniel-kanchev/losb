import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from losb.items import Article


class losbSpider(scrapy.Spider):
    name = 'losb'
    start_urls = ['https://www.losb.com/Resources/Blog-News']

    def parse(self, response):
        links = response.xpath('//a[@class="edn_readMore edn_readMoreButton"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@class="page"]/@href').getall()
        if next_page:
            yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="edn_articleTitle"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[4:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
