"""
北京市顺义区医院 肾脏内科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "北京市顺义区医院"
    name = doc('#summary > div.summary_con > div.doct_con > p:nth-child(1) > span').text()
    title = doc('#summary > div.summary_con > div.doct_con > p:nth-child(1)').text().strip(name)
    department = doc('#summary > div.summary_con > div.doct_con > p.szks_list > a > span').text()
    special = doc('#summary > div.summary_con > div.doct_con > p:nth-child(4)').text().strip('擅长：')
    resume = doc('div.Department_left > div.tab.mb20 > div>p').text().strip()
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
    week = {1: '周日', 2: '周一', 3: '周二', 4: '周三', 5: '周四', 6: '周五', 7: '周六', }
    outpatient_info = []
    morning = doc('div.PCDisplay tr:nth-child(2) > td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append(week[a + 1] + '上午' + b('span').text())

    afternoon = doc('div.PCDisplay tr:nth-child(3) > td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a + 2] + '下午' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('div.Min.mbt20 > ul > li > a').items()
    for item in links:
        link = 'http://www.hospitalshy.com' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.hospitalshy.com/Departments/Main/DoctorTeam/17'
    main(url)
