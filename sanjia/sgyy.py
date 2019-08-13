"""
北京大学首钢医院 肾脏内科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京大学首钢医院"
    name = doc('div.linkmap > span:nth-child(2) > a > span').text().strip('肾内科 ')
    title = doc('div.main_right_top > p:nth-child(5)').text() or '副主任医师'
    department = '肾内科'
    special = doc('div.main_right_top > p:nth-child(7)').text()
    resume = doc('div.main_rc_left > p.detail_p').text().strip() or doc(
        'body > div > div.mains > div > div > p:nth-child(3)').text()
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
    links = doc('ul.docteam_list.clearfix li a.doc_name').items()
    for item in links:
        link = 'http://www.sgyy.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.sgyy.com.cn/Html/Departments/Main/DoctorTeam_45.html'
    main(url)
