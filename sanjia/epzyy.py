"""
火箭军总医院 肾脏内科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "火箭军总医院"
    name = doc('div.doctor_top_content > h4 > a:nth-child(1)').text()
    title = doc('div.doctor_top_content > p:nth-child(3) > span:nth-child(1)').text().strip('职称：')
    department = doc('div.doctor_top_content > p:nth-child(3) > span:nth-child(2) > a').text()
    special = doc('div.doctor_top_content > p:nth-child(4)').text()
    resume = doc('div.doctor_bottom_content > p').text().strip()
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
    links = doc('div.main > ul > li > div > a').items()
    for item in links:
        link = 'http://www.epzyy.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.epzyy.cn/Html/Departments/Main/DoctorTeam_12.html'
    main(url)
