import scrapy
from urllib import parse
from ..items import MergeprojectItem
import re


class HongyouSpiderSpider(scrapy.Spider):
    name = 'hongyou_spider'
    allowed_domains = ['www.hongxiu.com']
    start_urls = ['https://www.hongxiu.com/']
    book_lists = ['继承亿万家产后我穿越了', '镇龙棺']
    search_url = 'https://www.hongxiu.com/search/'

    row_url = search_url + str(parse.quote(book_lists[0], encoding='utf-8'))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Referer': 'https://www.hongxiu.com/',
        'Host': 'www.hongxiu.com',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    meta_dict = {
        'b_name': book_lists[0]
    }

    def parse(self, response):
        if response.status == 200:
            yield scrapy.Request(self.row_url, callback=self.parse_url, headers=self.headers,meta=self.meta_dict)
        else:
            yield from super().start_requests()

    def parse_url(self, response):
        flag = False
        li_list = response.xpath('//div[@id="result-list"]/div[@class="book-img-text"]/ul/li')
        for li in li_list:
            b_name = li.xpath('./div[@class="book-mid-info"]/h4/a//text()')[0].extract()
            if b_name == response.meta['b_name']:
                flag = True
                next_url = li.xpath('./div[@class="book-mid-info"]/h4/a/@href')[0].extract()
                complete_url = "https:" + next_url
                yield scrapy.Request(complete_url, callback=self.parse_book_info, headers=self.headers,meta=response.meta)
                break
        if not flag:
            item = MergeprojectItem()
            item['b_name'] = response.meta['b_name']
            item['b_author'] = ''
            item['b_type'] = ''
            item['b_intro'] = ''
            yield item
        for b_name in self.book_lists[1:]:
            self.row_url = self.search_url + parse.quote(b_name, encoding='utf-8')
            self.meta_dict['b_name'] = b_name
            yield scrapy.Request(self.row_url,callback=self.parse_url,headers=self.headers,meta=self.meta_dict)

    def parse_book_info(self, response):
        item=MergeprojectItem()
        item['b_name'] = response.meta['b_name']
        author = response.xpath('//div[@class="book-info"]/h1/a/text()')[0].extract()
        item['b_author'] = author
        # xpath和xpathhelper不一样，如果选中的时多个对象,则必须对每个对象根据需要进行分离处理
        tags_li = response.xpath('//div[@class="book-info"]/p[@class="tag-box"]/span[@class="tag"]/i')
        tags_list = []
        for tag in tags_li:
            if len(tag.xpath('./@class')) == 0:
                tags_list.append(tag.xpath('./text()')[0].extract())
        b_type = '&'.join(tags_list)
        item['b_type'] = b_type
        b_intro = re.compile("['\n''    ''<br>''\u3000''\r'].*?").sub('', ''.join(response.xpath('//div[@class="book-info"]/p[@class="intro"]/text()').extract()))
        item['b_intro'] = b_intro
        yield item

