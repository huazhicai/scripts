"""
北京市大兴区人民医院 肾内科
"""

from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京市大兴区人民医院"
    name = doc('div.a_a > ul > li:nth-child(1)').text().strip('姓名：')
    title = doc('div.a_a > ul > li:nth-child(2)').text().strip('职称：')
    department = doc('div.a_a > ul > li:nth-child(3)').text().strip('科室：')
    resume = doc('div.a_b1').text().strip()
    special = re.search(r'擅长.*。', resume).group()
    outpatient_info = doc('div.a_a > ul > li:nth-child(7)').text().strip('出诊时间：')
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
    results = parse_detail(url)
    for result in results:
        # print(result)
        save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.dxqyy.com/html/2012-09/1657.html'
    main(url)
