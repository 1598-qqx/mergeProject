import scrapy
from urllib import parse
from ..items import MergeprojectItem
import re


class QidianSpiderSpider(scrapy.Spider):
    name = 'qidian_spider'
    allowed_domains = ['www.qidian.com', 'book.qidian.com']
    start_urls = ['https://www.qidian.com/']
    search_url = 'https://www.qidian.com/search?kw='
    book_lists = ['盗墓开局进入鲁王宫', '桃源小圣手', '千亿盛宠：闪婚老公超能干']
    row_url = search_url + str(parse.quote(book_lists[0], encoding='utf-8'))
    meta_dict = {
        'b_name': book_lists[0]
    }
    cookie_dict = {
        '_csrfToken': 'TncONJxjL6W4HdzI8lhARsXA8VLBv0pFZHk4vLGt', 'newstatisticUUID': '1610784484_103881423',
        'mrecUUID': '8240008f0d801de3533e22506612a666', 'qdrs': '0|3|0|0|1', 'qdgd': '1',
        'showSectionCommentGuide': '1', 'lrbc': '1014104227|450856481|0', 'rcr': '1014104227', 'hiijack': '0',
        'se_ref': 'baidu', 'se_ref_bid': '1022747201', '_yep_uuid': '1713c1f2-2dbb-9d8e-b72c-dfd86e65196c',
        'e2': '{"pid":"qd_p_qidian","eid":"","l1":2}', 'e1': '{"pid":"qd_p_qidian","eid":"qd_A13","l1":2}'
    }
    cookie_info_dict = {
        'e1': '{"pid":"qd_p_qidian","eid":"qd_A13","l1":2}', 'e2': '{"pid":"qd_P_Searchresult","eid":"qd_S05","l1":3}',
        '_yep_uuid': '0af1b8f7-42a9-ecc6-b686-9e48d17653cd', '_csrfToken': 'TncONJxjL6W4HdzI8lhARsXA8VLBv0pFZHk4vLGt',
        'newstatisticUUID': '1610784484_103881423', 'mrecUUID': '8240008f0d801de3533e22506612a666', 'qdrs': '0|3|0|0|1',
        'qdgd': '1', 'showSectionCommentGuide': '1', 'lrbc': '1014104227|450856481|0', 'rcr': '1014104227',
        'hiijack': '0'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
        'Referer': 'https://www.qidian.com/',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }
    def parse(self, response):
        if response.status == 200:
            yield scrapy.Request(self.row_url, callback=self.parse_info_url,headers=self.headers, cookies=self.cookie_dict,meta=self.meta_dict)
        else:
            yield from super().start_requests()

    def parse_info_url(self, response):
        # 逻辑问题,对书名列表中的每个书，都需要判断一个flag,而不是定义一个全局的flag
        flag = False
        item = MergeprojectItem()
        item['b_name'] = response.meta['b_name']
        item['b_author'] = ''
        item['b_type'] = ''
        item['b_intro'] = ''
        li_lists = response.xpath('//div[@id="result-list"]/div[@class="book-img-text"]/ul/li')
        if len(li_lists)>0:
            for li in li_lists:
                b_name = li.xpath('./div[@class="book-mid-info"]/h4/a//text()')[0].extract()
                if response.meta['b_name'] == b_name:
                    flag = True
                    next_info = li.xpath('./div[@class="book-mid-info"]/h4/a/@href')[0].extract()
                    complete_url = "https:" + next_info
                    yield scrapy.Request(complete_url,callback=self.parse_info,headers=self.headers, meta=response.meta, cookies=self.cookie_info_dict)
                    break
            if not flag:
                yield item
        else:
            yield item
        for b_name in self.book_lists[1:]:
            self.row_url = self.search_url + str(parse.quote(b_name, encoding='utf-8'))
            self.meta_dict['b_name'] = b_name
            yield scrapy.Request(self.row_url, callback=self.parse_info_url, meta=self.meta_dict, headers=self.headers,
                                 cookies=self.cookie_dict)

    def parse_info(self, response):
        item = MergeprojectItem()
        item['b_name'] = response.meta['b_name']
        b_type = ','.join(response.xpath('//div[@class="book-info "]/p[@class="tag"]//a/text()').extract())
        b_intro = re.compile("['\n''    ''<br>''\u3000']*?").sub('', response.xpath('//div[@class="book-intro"]/p/text()')[0].extract())
        item['b_author'] = ''
        item['b_type'] = b_type
        item['b_intro'] = b_intro
        yield item

