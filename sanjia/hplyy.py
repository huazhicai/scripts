"""
和平里医院 肾内科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding="gbk")
    file = os.path.basename(__file__)
    hospital = "和平里医院"
    name = doc('#doctor_content_name > ul > li > b').text()
    title = doc('#doctor_up > div.doctor_duan > ul:nth-child(2) > li:nth-child(2)').text()
    department = '肾内科'
    special = doc('#doctor_down > div:nth-child(1)').text()
    resume = doc('#doctor_down > div:nth-child(2)').text().strip()
    outpatient_info = doc('#doctor_up > div.doctor_content').text()
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
    url = 'http://www.hplyy.com/zj/zj125.htm'
    main(url)
