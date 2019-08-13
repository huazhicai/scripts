"""
解放军总医院第四医学中心 肾内科
"""

from multiprocessing.pool import Pool

from sanjia.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "解放军总医院第四医学中心"
    name = doc('div.doc_marginbox > ul > li:nth-child(1) > span').text()
    title = doc('div.doc_marginbox > ul > li:nth-child(1) > font').text()
    department = doc('div.doc_marginbox > ul > li:nth-child(2)').text().strip('科室')
    special = doc(' div.doc_marginbox > ul > li:nth-child(4)').text().strip('擅长：')
    resume = doc('#showexpdiv > ul > li.zj_jj > p:nth-child(1)').text().strip()
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
    morning = doc('#tab_body > tr:nth-child(1) > td').items()
    for a, b in enumerate(morning):
        if b('div'):
            outpatient_info.append(week[a] + '上午' + b('div').text())

    afternoon = doc('#tab_body > tr:nth-child(2) > td').items()
    for a, b in enumerate(afternoon):
        if b('div'):
            outpatient_info.append(week[a] + '下午' + b('div').text())

    noon = doc('#tab_body > tr:nth-child(3) > td').items()
    for a, b in enumerate(noon):
        if b('div'):
            outpatient_info.append(week[a] + '晚上' + b('div').text())
    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('#qwzj > div > a').items()
    for item in links:
        link = 'http://www.pla304hosptal.com' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.pla304hosptal.com/304hospital/o54/index.jhtml'
    main(url)
