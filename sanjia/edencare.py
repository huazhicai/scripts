"""
北京怡德医院 肾脏内科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "北京怡德医院"
    name = doc('div.ysgrym2 > span:nth-child(1)').text()
    title = doc('div.ysgrym2 > span.doctor1_2').text().split('/')[1]
    department = '肾脏内科'
    special = doc('div.ysgrym2 > span:nth-child(8)').text()
    resume = doc('div.ysgrym2 > span:nth-child(5)').text().strip()
    outpatient_info = parse_outpatient(doc)
    yield {
        'file': file,
        'hospital': hospital,
        'grade': '',
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
    morning = doc('div.ysgrym2 > table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('img'):
            outpatient_info.append(week[a] + '上午 ' + b('span').text())

    afternoon = doc('div.ysgrym2 > table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('img'):
            outpatient_info.append(week[a] + '下午 ' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('div.kszx5_all > div.zjjj40 > a').items()
    for item in links:
        link = 'http://www.edencare.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.edencare.com.cn/index.php?a=lists&catid=48'
    main(url)
