"""
广安门医院 肾病内科
"""

from sanjia.common import *


def parse_detail(link):
    doc = pq(link, headers=headers, encoding='gbk')
    file = os.path.basename(__file__)
    hospital = "广安门医院"
    name = doc('div.colR770.kslb > div.kslb02 > dl:nth-child(2) > dd').text()
    title = doc('div.colR770.kslb > div.kslb02 > dl:nth-child(4) > dd').text()
    department = "肾病科"
    special = doc('div.colR770.kslb > div.kslb02 > dl:nth-child(5) > dd').text()
    resume = doc('div.colR770.kslb > div.kslb03 > span').text().strip()
    outpatient_info = [x.text() for x in doc('div.colR770.kslb > div.kslb02 > dl:nth-child(6) > dd').items()]
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
    doc = pq(url, headers=headers)
    links = doc('div.kslb01 > table tr > td > font > a').items()
    for item in links:
        link = 'http://www.gamhospital.ac.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.gamhospital.ac.cn/kssz/lcks/sbk/kszj/'
    main(url)
