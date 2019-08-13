"""
航空总医院 肾内科
"""

from sanjia.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "航空总医院"
    name = doc('div.ask_left > div.title_all > h2').text()
    title = doc('#zoom > div > dl > dd:nth-child(4)').text().strip('职称：')
    department = '肾内科'
    special = doc('#zoom > div > dl > dd:nth-child(7)').text().strip('专业特长：')
    resume = doc('#zoom > p').text()
    outpatient_info = doc('#zoom > div > dl > dd:nth-child(6) > span').text()
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
    links = doc('#zoom > ul > li > h2 > a').items()
    for item in links:
        link = 'http://www.hkzyy.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.hkzyy.com.cn/Html/Departments/Main/DoctorTeam_33.html'
    main(url)
