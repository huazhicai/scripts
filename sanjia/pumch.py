"""
北京协和医院 肾内科
"""

from multiprocessing.pool import Pool

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京协和医院"
    name = doc('div.dorname > div.title1').text().strip('查看科室更多医生')
    title = doc('div.dorname > div:nth-last-child(2)').text()
    department = '肾内科'
    special = doc('div.dorname > div:nth-last-child(1)').text().strip('擅长 : ')
    resume = doc('div.block div.desc').text().strip()
    outpatient_info = None
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


def main(url):
    doc = pq(url)
    links = doc('div.list.clearfix div.item a').items()
    for item in links:
        link = 'https://www.pumch.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    links = ['https://www.pumch.cn/department_shennk/doctor/p/{}.html'.format(page) for page in range(1, 5)]
    pool = Pool()
    pool.map(main, links)
