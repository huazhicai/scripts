"""
北京世纪地坛医院 肾脏内科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "北京世纪地坛医院"
    name = doc('div.doct_coninner p:nth-child(1) span').text()
    title = doc('#summary > div > div.doct_con > div > p:nth-child(1)').text().strip(name)
    department = doc('#summary > div > div.doct_con > div > p.szks_list > a > span').text()
    special = doc('#summary > div > div.doct_con > div > div > p').text()
    resume = doc('div.tab_box p').text().strip()
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
            outpatient_info.append(week[a-1]+'上午 '+b('span').text())

    afternoon = doc('div.PCDisplay > table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a]+'下午 '+b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('li.doct_li a.doct_img').items()
    for item in links:
        link = 'http://www.bjsjth.cn' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.bjsjth.cn/Html/Departments/Main/DoctorTeam_1000222.html'
    main(url)
