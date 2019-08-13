"""
北京大学第一医院 肾脏内科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京大学第一医院"
    name = doc('div.doct_con p:nth-child(1) span').text()
    title = doc('div.doct_con p:nth-child(1)').text().strip(name)
    department = doc('div.doct_con > p.szks_list > a > span').text()
    special = doc('div.doct_con > div.doctor_specialty > span:nth-child(2)').text()
    resume = doc('div.tab.mb20 div.tab_box p').text().strip()
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
    week = {1: '周日', 2: '周一', 3: '周二', 4: '周三', 5: '周四', 6: '周五', 7: '周六', }
    outpatient_info = []
    morning = doc('#con_tableb_1 tr:nth-child(2) > td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append(week[a] + '上午' + b('span').text())

    afternoon = doc('#con_tableb_1 tr:nth-child(3) > td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a] + '下午' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('ul.doctorList.mt15 li a.doc_name').items()
    for item in links:
        link = 'https://www.pkufh.com' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'https://www.pkufh.com/Html/Departments/Main/DoctorTeam_9.html'
    main(url)
