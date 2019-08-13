"""
北京中医药大学东方医院 肾病科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "北京中医药大学东方医院"
    name = doc('ul.w260.left > div > dl:nth-child(2) > dd > strong').text()
    title = doc('ul.w260.left > div > dl:nth-child(6) > dd').text()
    department = doc('ul.w260.left > div > dl:nth-child(7) > dd').text()
    special = doc('ul.w720.right > ul:nth-child(4)').text()
    resume = doc('ul.w720.right > ul:nth-child(6)').text().strip()
    outpatient_info = re.findall(r'门诊.*', resume)
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
    links = doc('div.kszj02d > div > div > dl > dd > ul > a').items()
    for item in links:
        link = 'http://www.dongfangyy.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.dongfangyy.com.cn/doctor/list/50.html'
    main(url)
