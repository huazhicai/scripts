"""
宣武医院 肾科
"""

from sanjia.common import *
from lxml import etree


def parse_detail(link):
    html = get_resp(link)
    doc = etree.HTML(html)
    file = os.path.basename(__file__)
    hospital = "宣武医院"
    name = doc.xpath('//div[@class="doc_inct"]/h2/text()')[0]
    title = doc.xpath('//div[@class="doc_cont"]/p/span[contains(text(), "职称：")]/parent::*/text()')
    department = doc.xpath('/html/body/div/div[4]/div[2]/div[2]/div[1]/div[2]/p[1]/a')
    special = doc.xpath('//div[@class="doc_cont"]/p/span[contains(text(), "专长：")]/parent::*/text()')
    resume = doc.xpath('//div[@class="jianj_box"]/p/text()')
    outpatient_info = doc.xpath('//div[@class="doc_cont"]//div[@class="PCDisplay"]/span[position()>1]/text()')
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
    links = doc('ul.doctorList > li > a:nth-child(1)').items()
    for item in links:
        link = 'http://sk.xwhosp.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://sk.xwhosp.com.cn/Html/Departments/Main/DoctorTeam_10000010.html'
    main(url)
