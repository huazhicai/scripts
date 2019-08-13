"""
北京大学人民医院 肾内科
"""

from multiprocessing.pool import Pool

from lxml import etree
from sanjia.common import *


def parse_detail(link):
    html = get_resp(link)
    doc = etree.HTML(html)
    file = os.path.basename(__file__)
    hospital = "北京大学人民医院"
    name = doc.xpath('//div[@class="content"]/b[@class="yname"]/text()')[0]
    title = doc.xpath('//div[@class="content"]/text()')[6]
    department = doc.xpath('//div[@class="content"]/text()')[2]
    special = doc.xpath('//div[@class="content"]/text()')[8]
    resume = '.'.join(doc.xpath('//div[@class="xkscon"]/p/text()'))
    outpatient_info = doc.xpath('//div[@class="content"]/text()')[10].strip().split('，')
    yield {
        'file': file,
        'hospital': hospital,
        'grade': '三甲',
        'name': name,
        'title': title,
        'department': department,
        'special': special,
        'resume': resume,
        'outpatient_info': outpatient_info,
        'link': link
    }


def main(url):
    doc = pq(url)
    links = doc('#DoctorList tr > td:nth-child(1) > a').items()
    for item in links:
        link = 'http://www.pkuph.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    links = ['http://www.pkuph.cn/Article/Index/department/id/115/cid/115/type/2/p/{}.html'.format(page) for page in
             range(1, 3)]
    pool = Pool()
    pool.map(main, links)
