"""
中国康复研究中心 肾内科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "中国康复研究中心"
    name = doc('#jianjie > div.ks_jj_con > div.doctor_message > div > dl > dt > span').text()
    title = doc('#jianjie > div.ks_jj_con > div.doctor_message > div > dl > dd:nth-child(2)').text().strip('职称：')
    department = '肾内科'
    special = doc('#jianjie > div.ks_jj_con > div.doctor_message > div > dl > dd:nth-child(5)').text()
    resume = doc('#Descri > p').text().strip()
    outpatient_info = doc('div.PCDisplay span:not(.ChuZhen)').text()
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
    results = parse_detail(url)
    for result in results:
        # print(result)
        save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.crrc.com.cn/Html/Doctors/Main/Index_339.html'
    main(url)
