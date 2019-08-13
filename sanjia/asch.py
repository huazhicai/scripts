"""
航天中心医院 肾内科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "航天中心医院"
    name = doc('ul.w289.left > div:nth-child(2) > dl:nth-child(2) > dd > strong').text()
    title = doc('ul.w289.left > div:nth-child(2) > dl:nth-child(6) > dd').text()
    department = doc('ul.w289.left > div:nth-child(2) > dl:nth-child(7) > dd').text()
    special = doc('ul.w688.right > ul:nth-child(3)').text()
    resume = doc('ul.w688.right > ul:nth-child(5)').text().strip()
    outpatient_info = parse_outpatient(doc)
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


# 解析出诊信息
def parse_outpatient(doc):
    week = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    outpatient_info = []
    morning = doc('ul.w688.right > div > table tr:nth-child(1) td').items()
    for a, b in enumerate(morning):
        if b('img'):
            outpatient_info.append(week[a] + '上午' + b('img').text())

    afternoon = doc('ul.w688.right > div > table tr:nth-child(2) td').items()
    for a, b in enumerate(afternoon):
        if b('img'):
            outpatient_info.append(week[a] + '下午' + b('img').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('div.catalog04.catalog04a > dl > dd > ul > a').items()
    for item in links:
        link = 'http://www.asch.net.cn' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.asch.net.cn/departments/article/55.html'
    main(url)
