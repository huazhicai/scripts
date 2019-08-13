"""
煤炭总医院 肾病科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "煤炭总医院"
    name = doc('#summary > div.summary_con > div.doct_con > p:nth-child(1) > span').text()
    title = doc('#summary > div.summary_con > div.doct_con > p:nth-child(2) > span').text()
    department = '肾内科'
    special = doc('#summary > div.summary_con > div.doct_con > div > div > p').text()
    resume = doc('div.Department_left > div.tab.mb20.mt5 > div:nth-child(2) > div > p').text().strip()
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
    morning = doc('div.PCDisplay table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append(week[a - 1] + '上午' + b('span').text())

    afternoon = doc('div.PCDisplay table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a] + '下午' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('div.Min.mbt20 > ul > li a.doct_img').items()
    for item in links:
        link = 'http://www.mtzyy.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.mtzyy.com.cn/Html/Departments/Main/DoctorTeam_100011.html'
    main(url)
