"""
北京中医药大学第三附属医院 肾脏内科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京中医药大学第三附属医院"
    name = doc('div.doctor_con > dl > dt > span').text()
    title = doc('div.doctor_con > dl > dd:nth-child(2)').text().strip('职称：')
    department = '肾病科'
    special = doc('div.doctor_con > dl > dd:nth-child(5)').text().strip('专业特长：')
    resume = doc('#Descri > p').text().strip()
    outpatient_info = doc('div.PCDisplay span:not(:nth-child(1))').text()
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
    links = doc('li.Depth1.hover > ul > li > a').items()
    for item in links:
        link = 'http://www.zydsy.com' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.zydsy.com/Html/Departments/Main/Index_101.html#doctor'
    main(url)
