"""
北京友谊医院 肾病内科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京友谊医院"
    name = doc('body > div > div.main > div > div.ask_left > div > div.title_all > h2').text()
    title = doc('#jianjie > div.ks_jj_con > div.doctor_message > div > dl > dd:nth-child(2)').text().strip('职称：')
    department = doc('div.department_l > p > a.pic-name').text()
    special = doc('#jianjie > div.ks_jj_con > div.doctor_message > div > dl > dd:nth-child(4)').text()
    resume = doc('#Descri > p:nth-child(1)').text().strip()
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
        'link': link,
    }


# 解析出诊信息
def parse_outpatient(doc):
    week = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    outpatient_info = []
    morning = doc('div.PCDisplay > table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if a < 8 and b('span'):
            outpatient_info.append(week[a] + '上午' + b('span').text())

    afternoon = doc('div.PCDisplay > table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if a < 8 and b('span'):
            outpatient_info.append(week[a] + '下午' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('#team > ul > li a.doc_name').items()
    for item in links:
        link = 'http://www.bfh.com.cn' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.bfh.com.cn/Html/Doctors/Main/Index_471.html'
    main(url)
