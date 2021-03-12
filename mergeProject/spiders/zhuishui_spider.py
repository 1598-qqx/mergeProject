import scrapy
import re
from ..items import MergeprojectItem


class ZhuishuiSpiderSpider(scrapy.Spider):
    name = 'zhuishui_spider'
    allowed_domains = ['m.zhuishubox.com']
    start_urls = ['https://m.zhuishubox.com/']
    base_url = 'https://m.zhuishubox.com'
    search_url = 'https://m.zhuishubox.com/s.php'
    book_lists = ['一世婚宠：总裁娇妻萌萌哒', '锦绣空间之喜事临门']
    book_authors = ['桃灼灼', '福娘']
    form_data = {
        'type': 'articlename',
        'submit': '',
        's': book_lists[0].encode('gbk')
    }
    # cookie在本地保存7天，以后使用需要更换
    cookie_dict = {
        'Hm_lvt_8b3622adf18e63efaee65d63b8ccef5d': '1612324161,1613988964',
        'Hm_lpvt_8b3622adf18e63efaee65d63b8ccef5d': '1613988964',
        'PHPSESSID': '73e16383870f68f851db1e872d489cdc'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Referer': 'https://m.zhuishubox.com/',
        'content-type': 'application/x-www-form-urlencoded'
    }
    meta_dict = {
        'b_name': book_lists[0],
        'b_author': book_authors[0]
    }
    headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    cookie_get_dict = {
        'Hm_lvt_8b3622adf18e63efaee65d63b8ccef5d': '1612324161,1613988964',
        'PHPSESSID': '73e16383870f68f851db1e872d489cdc',
        'Hm_lpvt_8b3622adf18e63efaee65d63b8ccef5d': '1613992767'
    }

    def parse(self, response):
        if response.status == 200:
            yield scrapy.FormRequest(self.search_url, callback=self.parse_info, formdata=self.form_data, cookies=self.cookie_dict, meta=self.meta_dict, headers=self.headers)
        else:
            yield from super().start_requests()

    def parse_info(self, response):
        p_lists = response.xpath('//div[@class="cover"]/p')
        if len(p_lists)>0:
            for p in p_lists:
                p_name = re.compile("['\r''\n'' '].*?").sub('',p.xpath('./a[2]/text()')[0].extract())
                p_author = re.compile("['\r''\n'' '].*?").sub('',p.xpath('./a[3]/text()')[0].extract())
                if p_name == response.meta['b_name'] and p_author == response.meta['b_author']:
                    next_url = p.xpath('./a[2]/@href')[0].extract()
                    complete_url = self.base_url + next_url
                    yield scrapy.Request(complete_url, callback=self.parse_complete_info, headers=self.headers_get, cookies=self.cookie_get_dict, meta=response.meta)
                    break
        else:
            item = MergeprojectItem()
            item['b_name'] = response.meta['b_name']
            item['b_author'] = response.meta['b_author']
            item['b_type'] = ''
            item['b_intro'] = ''
            yield item
        for b_name, b_author in zip(self.book_lists[1:],self.book_authors[1:]):
            self.form_data['s'] = b_name.encode('gbk')
            self.meta_dict['b_name'] = b_name
            self.meta_dict['b_author'] = b_author
            yield scrapy.FormRequest(self.search_url, formdata=self.form_data,meta=self.meta_dict,cookies=self.cookie_dict, headers=self.headers,callback=self.parse_info)

    def parse_complete_info(self, response):
        b_intro = re.compile("['\r''\n'' '].*?").sub('', response.xpath('//div[@class="intro_info"]/text()')[0].extract())
        b_type = response.xpath('//div[@class="block"]/div[@class="block_txt2"]/p[3]/a/text()')[0].extract()
        item = MergeprojectItem()
        item['b_name'] = response.meta['b_name']
        item['b_author'] = response.meta['b_author']
        item['b_intro'] = b_intro
        item['b_type'] = b_type
        yield item
