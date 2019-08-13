"""
解放军第306医院 肾内科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "解放军第306医院"
    grade = '三甲'
    resume = doc('div.gk-main-r.sheb-main-r > div > p:nth-child(3) > span').text().strip()
    name = doc('div.gk-main-r.sheb-main-r > div > h3').text()
    title = re.search(r'，(.*医师)', resume)
    title = title.group(1) if title else ''
    department = doc('div.gk-main-r.sheb-main-r > span > em').text()
    special = doc('#specialty > p:nth-last-child(1)').text()
    outpatient_info = parse_outpatient(doc)
    yield {
        'file': file,
        'hospital': hospital,
        'grade': grade,
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
            outpatient_info.append(week[a - 1] + '上午 ' + b('span').text())

    afternoon = doc('div.PCDisplay > table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a] + '下午 ' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('div.mz-yisheng > ul > li> p > a.a-tit').items()  # 医师详情页链接
    for item in links:
        link = 'http://www.306.cn' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.306.cn/ksjs/show/180.html'
    main(url)
