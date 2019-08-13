"""
北京301医院 肾脏病科
"""
from multiprocessing.pool import Pool

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "北京301医院"
    grade = '三甲'
    name = doc('#showexpdiv > ul > li.zj_xm > strong').text().strip('姓名：')
    title = doc('#showexpdiv > ul > li.zj_xm').text().split('\xa0\xa0\xa0\xa0\xa0\xa0')[1].strip('职称：')
    department = doc('#showexpdiv > ul > li.zj_xm').text().split('\xa0\xa0\xa0\xa0\xa0\xa0')[2].strip('科室：')
    special = doc('div.zj_ys_b>p').text()
    resume = doc('#showexpdiv > ul > li.zj_jj > p:nth-child(1)').text().strip()
    outpatient_info = [item('td').text() for item in doc('div.zj_ys_b > table > tr').items()]
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


def main(url):
    doc = pq(url)
    links = doc('ul.ks_piclist1>li>a').items()  # 医生详情页链接
    for item in links:
        link = 'http://www.301hospital.mil.cn/' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    links = ['http://www.301hospital.mil.cn/web/ksexpert/myhcv/62.html?page={}'.format(page) for page in range(1, 3)]
    pool = Pool()
    pool.map(main, links)
