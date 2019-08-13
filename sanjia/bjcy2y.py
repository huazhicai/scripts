"""
北京市第一中西结合医院 肾内科
"""
import json
from sanjia.utils.common import *


def parse_detail(url):
    resp = get_resp(url)
    doc = pq(resp)
    file = os.path.basename(__file__)
    hospital = '北京市第一中西结合医院'
    name = doc('ul.w225.left > div > dl:nth-child(2) > dd > strong').text()
    title = doc('div.experts01 dl:nth-child(6).experts01b dd').text()
    department = doc('div.experts01 dl:nth-child(7) dd').text()
    special = doc('body > div > div.main_content > ul.w745.right > ul:nth-child(3) > p').text()
    resume = doc('body > div > div.main_content > ul.w745.right > ul:nth-child(5) > p').text()
    outpatient_info = parse_outpatient(doc)
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
        'link': url
    }


def parse_outpatient(doc):
    week = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    outpatient_info = []
    morning = doc('div.clear tbody tr:nth-child(1) td').items()
    for a, b in enumerate(morning):
        if b('img'):
            outpatient_info.append(week[a]+'上午')

    afternoon = doc('div.clear tbody tr:nth-child(2) td').items()
    for a, b in enumerate(afternoon):
        if b('img'):
            outpatient_info.append(week[a]+'下午')

    return outpatient_info


def write_to_file(content):
    with open('.'.join([os.path.splitext(__file__)[0], 'txt']), 'a', encoding='utf-8') as f:
        f.write(json.dumps(content, ensure_ascii=False) + '\n')


def main(url):
    doc = pq(url)
    links = doc('div.catalog04.catalog04a a.link08').items()
    for url in links:
        link = 'http://www.bjcy2y.com' + url.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.bjcy2y.com/departments/article/355.html?pg=2'
    main(url)
