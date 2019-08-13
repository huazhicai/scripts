"""
北京潞河医院 肾病科
"""



from sanjia.utils.common import *


def get_detail_url(html):
    doc = pq(url)
    links = doc('').items()
    return links


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京潞河医院"
    name = doc('div.doctor_message > div > dl > dt > span').text()
    title = doc('div.doctor_message > div > dl > dd:nth-child(3)').text().strip('职称：')
    department = doc('div.doctor_message > div > dl > dd:nth-child(2) > a').text()
    special = doc('div.doctor_message > div > dl > dd:nth-child(6)').text().strip('专业特长：')
    resume = doc('#Descri > p').text().strip()
    outpatient_info = doc('div.doctor_message > div > dl > dd:nth-child(5) > div > span:nth-child(2)').text()
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
    links = doc('#con_setTab_1 > ul > div:nth-child(12) > h2:nth-child(2) > ul > li > a').items()
    for item in links:
        link = 'https://www.luhehospital.com' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'https://www.luhehospital.com/Html/Hospitals/Doctors/Overview321.html'
    main(url)
