"""
北京积水潭医院 肾病科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京积水潭医院"
    name = doc('body > div > div > div > div.linkMap > a:nth-child(6) > span').text()
    title = doc('div.doctor_con > p:nth-child(3)').text().strip('职称：')
    department = doc('div.doctor_con > p:nth-child(4) a').text()
    special = doc('div.doctor_con > p:nth-last-child(2)').text().strip('专长：')
    resume = doc('div.doc_con p').text().strip()
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
    week = {2: '周一', 3: '周二', 4: '周三', 5: '周四', 6: '周五', 7: '周六', 8: '周日'}
    outpatient_info = []
    morning = doc('div.PCDisplay table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append(week[a] + '上午' + b('span').text())

    afternoon = doc('div.PCDisplay table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a + 1] + '下午' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('ul.docteam_list.clearfix li a.doc_name').items()
    for item in links:
        link = 'http://www.jst-hosp.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.jst-hosp.com.cn/Html/Departments/Main/DoctorTeam_509.html'
    main(url)
