# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class MergeprojectPipeline:
    def process_item(self, item, spider):
        if item['b_type'] == '':
            with open('./qingdou/test_not_have.csv', 'a+') as f:
                s = str(item['b_name']) + ',' + str(item['b_author'])+'\n'
                f.write(s)
        else:
            with open('./qingdou/test_have.csv', 'a+') as f:
                s = str(item['b_name']) + ',' + str(item['b_author']) + ',' + str(item['b_type']) + ',' \
                    + str(item['b_intro']) + '\n'
                f.write(s)
        return item
