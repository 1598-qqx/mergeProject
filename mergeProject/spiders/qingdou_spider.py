import scrapy
from ..items import MergeprojectItem
import re


class QingdouSpiderSpider(scrapy.Spider):
    name = 'qingdou_spider'
    allowed_domains = ['www.qingdou.net']
    start_urls = ['https://www.qingdou.net/']
    search_url = 'https://www.qingdou.net/search.html'
    base_url = 'https://www.qingdou.net'
    book_lists = ['千亿盛宠：闪婚老公超能干', '一世婚宠：总裁娇妻萌萌哒', '盛世闪婚：总裁有点贪', '无上神帝']
    book_authors = ['许微笑', '桃灼灼', '鸭蛋', '潇湘羽墨']
    form_data = {
        'searchkey': book_lists[0].encode('utf-8')
    }
    meta_dict = {
        'b_name': book_lists[0],
        'b_author': book_authors[0]
    }
    # cookie在本地保存7天，以后使用需要更换
    cookie_dict_post = {
        '__cfduid': 'd96794908471ed9d4a77cf1518233fb0f1612419526',
        'Hm_lvt_379406288c8a13d427c882417433390a': '1612419528,1612419778,1613981382',
        'Hm_lpvt_379406288c8a13d427c882417433390a': '1613982304'
    }
    cookie_dict_get = {
        '__cfduid': 'd96794908471ed9d4a77cf1518233fb0f1612419526',
        'Hm_lvt_379406288c8a13d427c882417433390a': '1612419528,1612419778,1613981382',
        'Hm_lpvt_379406288c8a13d427c882417433390a': '1613984233'
    }
    headers_post = {
        'referer': 'https://www.qingdou.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded'
    }
    headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Referer': 'https://www.qingdou.net/search.html'
    }

    def parse(self, response):
        if response.status == 200:
            yield scrapy.FormRequest(self.search_url, callback=self.parse_url, formdata=self.form_data, cookies=self.cookie_dict_post, headers=self.headers_post, meta=self.meta_dict)
        else:
            yield from super().start_requests()

    def parse_url(self, response):
        alists = response.xpath('//div[@id="alist"]/div[@id="alistbox"]')
        if len(alists)>0:
            for al in alists:
                title = al.xpath('./div[@class="info"]/div[@class="title"]/h2/a/text()')[0].extract()
                author = al.xpath('./div[@class="info"]/div[@class="title"]/span/a/text()')[0].extract()
                if title == response.meta['b_name'] and author == response.meta['b_author']:
                    next_url = al.xpath('./div[@class="info"]/div[@class="title"]/h2/a/@href')[0].extract()
                    complete_url = self.base_url + next_url
                    yield scrapy.Request(complete_url, callback=self.parse_book_info, headers=self.headers_get,
                                         cookies=self.cookie_dict_get, meta=response.meta)
                    break
        else:
            item = MergeprojectItem()
            item['b_name'] = response.meta['b_name']
            item['b_author'] = response.meta['b_author']
            item['b_type'] = ''
            item['b_intro'] = ''
            yield item
        for b_name, b_author in zip(self.book_lists[1:], self.book_authors[1:]):
            self.meta_dict['b_name'] = b_name
            self.meta_dict['b_author'] = b_author
            self.form_data['searchkey'] = b_name.encode('utf-8')
            yield scrapy.FormRequest(self.search_url, formdata=self.form_data, callback=self.parse_url, cookies=self.cookie_dict_post, headers=self.headers_post, meta=self.meta_dict)

    def parse_book_info(self, response):
        item = MergeprojectItem()
        b_type = response.xpath('//ul[@class="bread-crumbs"]/li[2]/a/text()')[0].extract()
        b_intro = re.compile("['\r''\n''\t'' '].*?").sub('', response.xpath('//div[@class="intro"]/text()')[0].extract())
        item['b_name'] = response.meta['b_name']
        item['b_author'] = response.meta['b_author']
        item['b_type'] = b_type
        item['b_intro'] = b_intro
        yield item

