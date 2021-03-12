import scrapy
from ..items import MergeprojectItem
import re


class WeifengSpiderSpider(scrapy.Spider):
    name = 'weifeng_spider'
    request_url = 'https://www.wfxs.tw/s.html'
    allowed_domains = ['www.wfxs.tw']
    start_urls = ['https://www.wfxs.tw/']
    book_list = ['千亿盛宠：闪婚老公超能干', '豪门暖婚之夫人说了算', '医妃天下：王爷，请自重']
    author_list = ['许微笑', '花耶花耶', '香林']
    row_meta_dict = {
        'b_name': book_list[0],
        'b_author': author_list[0]
    }
    data_dict = {
            'type': 'articlename',
            's': book_list[0].encode('utf-8')
        }
    # cookie在本地保存7天，以后使用需要更换
    cookie_dict = {'__gads': 'ID=28cf13685d935f5a-222299f00fc60014', 'T': '1613721702', 'RT': '1613721702', 'S': 'ALNI_MaOAfcpj3yOhg8FohIKIIeX2z09Yg'}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://www.wfxs.tw/',
        'Origin': 'https://www.wfxs.tw',
        'Host': 'www.wfxs.tw'
    }

    def parse(self, response):
        if response.status == 200:
            yield scrapy.FormRequest(self.request_url, formdata=self.data_dict, headers=self.headers,
                                     cookies=self.cookie_dict, callback=self.parse_post, meta=self.row_meta_dict)
        else:
            yield from super().start_requests()

    def parse_post(self, response):
        """
        在这里定义itme对象的数据解析内容
        :param response:
        :return:
        """
        item = MergeprojectItem()
        item['b_name'] = response.meta['b_name']
        item['b_author'] = response.meta['b_author']
        item['b_type'] = ''
        item['b_intro'] = ''
        if response.status == 200:
            dl_list = response.xpath('//div[@id="sitembox"]/dl')
            for dl in dl_list:
                extract_b_name = dl.xpath('./dd[1]/h3/a/text()')[0].extract()
                extract_b_author = dl.xpath('./dd[@class="book_other"]/span[1]/text()')[0].extract()
                if extract_b_name == response.meta['b_name'] and extract_b_author == response.meta['b_author']:
                    b_type = dl.xpath('./dd[@class="book_other"]/span[3]/text()')[0].extract()
                    b_intro = re.compile("['\r''\n'' '].*?").sub('', dl.xpath('./dd[@class="book_des"]/text()')[0].extract())
                    item['b_type'] = b_type
                    item['b_intro'] = b_intro
                    break
        yield item
        for n_name, n_author in zip(self.book_list[1:], self.author_list[1:]):
            meta_data = {
                'b_name': n_name,
                'b_author': n_author
            }
            self.data_dict['s'] = n_name.encode('utf-8')
            yield scrapy.FormRequest(self.request_url, callback=self.parse_post, cookies=self.cookie_dict, meta=meta_data,
                                     formdata=self.data_dict, headers=self.headers)
