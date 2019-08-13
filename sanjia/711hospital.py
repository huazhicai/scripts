"""
航天总医院 肾内科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "航天总医院"
    grade = '三级'
    name = doc('div.linkmap > dl > dd > p > a:nth-child(5) > span').text()
    title = doc('div.main > div > div.doctor_con > p:nth-child(3)').text().strip('职称：')
    department = doc('div.main > div > div.doctor_con > p:nth-child(4) > a').text()
    special = doc('div.main > div > div.doctor_con > p:nth-child(5)').text().strip('专长：')
    resume = doc('div.main > div > div:nth-child(5) > p:nth-child(4)').text().strip()
    outpatient_info = ''
    yield {
        'file': file,
        'hospital': hospital,
        'grade': grade,
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
    links = doc('div.main > div > div > ul > li > div > a').items()
    for item in links:
        link = 'http://www.711hospital.com' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.711hospital.com/Html/Departments/Main/DoctorTeam_42.html'
    main(url)
