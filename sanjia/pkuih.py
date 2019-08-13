"""
北京大学国际医院 肾脏内科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "北京大学国际医院"
    name = doc('div.content.w972.fix > div.left1 > div > div > div.Doctor_nr > p').text()
    title = re.search(r'[副|主].*', name).group()
    name = name.strip(title)
    department = '肾脏内科'
    special = doc('div.content.w972.fix > div.left1 > div > ul > li:nth-child(2) > p').text()
    resume = doc('div.content.w972.fix > div.left1 > div > ul > li:nth-child(3) > p').text().strip()
    outpatient_info = doc('div.content.w972.fix > div.left1 > div > ul > li:nth-child(1) > p').text()
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
    links = doc('div.Professional_team.fix > ul > li > a').items()
    for item in links:
        link = 'https://www.pkuih.edu.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'https://www.pkuih.edu.cn/page/dept.html?_page.id=Page_ff80808152430b7c01524314b75b0015&_dept.id=Department_8a83988252f0a1d50152f0a32df80013'
    main(url)
