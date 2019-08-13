"""
广安门医院南区 肾病科
"""
from multiprocessing.pool import Pool
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, headers=headers)
    file = os.path.basename(__file__)
    hospital = "广安门医院南区"
    name = doc('div.physicians > div:nth-child(1) > div:nth-child(2) > span > strong').text()
    info = doc('div.physicians > div:nth-child(1) > div:nth-child(2) > span').text()
    title = re.search(r'职称：(.*)', info).group(1)
    department = re.search(r'科室：(.*)', info).group(1)
    special = re.search(r'专长：(.*)', info).group(1)
    resume = doc('div.physicians > div:nth-child(3) > span').text().strip()
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
    morning = doc('table.ke-zeroborder tr:nth-child(2) > td').items()
    for a, b in enumerate(morning):
        if b('td.txt_clo'):
            outpatient_info.append(week[a] + '上午 ' + b('td.txt_clo').text())

    afternoon = doc('table.ke-zeroborder tr:nth-child(3) > td').items()
    for a, b in enumerate(afternoon):
        if b('td.txt_clo'):
            outpatient_info.append(week[a] + '下午 ' + b('td.txt_clo').text())

    return outpatient_info


def main(url):
    doc = pq(url, headers=headers)
    links = doc('div.introduce > div.td_list > table > tr > td:nth-child(1) > a').items()
    for item in links:
        link = 'http://www.gamhnq.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.gamhnq.cn/tdlb/index.aspx?nodeid={}'
    # main(url)
    pool = Pool()
    links = [url.format(nodeid) for nodeid in range(355, 357)]
    pool.map(main, links)
