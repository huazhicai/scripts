"""
平谷区医院 肾病科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "平谷区医院"
    name = doc('div.main_left_top > div > h4').text()
    title = doc('div.main_left_top > div > p:nth-child(3) > span:nth-child(1)').text().strip('职称：')
    department = doc('div.main_left_top > div > p:nth-child(3) > span:nth-child(2) > a').text()
    special = doc('div.main_left_top > div > p:nth-child(4)').text().strip('特长：')
    resume = doc('div.main_left_top > div > div.jianj > p').text().strip()
    outpatient_info = []
    yield {
        'file': file,
        'hospital': hospital,
        'grade': '三级',
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
    links = doc('div.blue_white_block > ul > li > h2 > a').items()
    for item in links:
        link = 'http://www.pgyy.com' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.pgyy.com/Html/Departments/Main/DoctorTeam_42.html'
    main(url)
