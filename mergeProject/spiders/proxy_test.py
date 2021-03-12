import scrapy


class ProxyTestSpider(scrapy.Spider):
    name = 'proxy_test'
    allowed_domains = ['icanhazip.com']
    start_urls = ['http://icanhazip.com/']

    def parse(self, response):
        pass
