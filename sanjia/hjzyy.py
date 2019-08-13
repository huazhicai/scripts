"""
海军总医院 肾脏内科
"""

from sanjia.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "海军总医院"
    name = doc('div.linkmap a span.navspan').text()
    title = doc('#change > div.main > div > div.article_area > p:nth-child(2) > span').text()
    department = doc('#change > div.main > div > div.article_area > p:nth-child(3) > span > a').text()
    special = doc('#change > div.main > div > div.article_area > p:nth-child(4)').text().strip('擅长：')
    resume = doc('#change > div.main > div > div:nth-child(4) > p').text().replace('\xa03', '')
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
        'link': link
    }


# 解析出诊信息
def parse_outpatient(doc):
    week = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    outpatient_info = []
    morning = doc('div.PCDisplay > table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append(week[a - 1] + '上午' + b('span').text())

    afternoon = doc('div.PCDisplay > table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a] + '下午' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('div.docteam_cont a.doc_name').items()
    for item in links:
        link = 'http://www.hjzyy.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.hjzyy.com.cn/Html/Departments/Main/DoctorTeam_4.html'
    main(url)
