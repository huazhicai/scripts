"""
北京同仁医院 肾病科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京同仁医院"
    name = doc('div.doctor_con dl dt span').text()
    title = doc('div.doctor_con dl dd:nth-child(2)').text().strip('职称：')
    department = "肾内科"
    special = None
    resume = doc('div.doctor_con dl dd:nth-last-child(1)').text().strip('个人简介：')
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
    week = {6: '周四', 7: '周五', 8: '周六', 2: '周日', 3: '周一', 4: '周二', 5: '周三'}
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
    links = doc('#team > ul > li a.doc_name').items()
    for item in links:
        link = 'http://www.trhos.com' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.trhos.com/Html/Doctors/Main/Index_777.html'
    main(url)
