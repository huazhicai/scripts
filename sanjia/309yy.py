"""
解放军总医院第八医学中心 肾脏病科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "解放军总医院第八医学中心"
    grade = '三甲'
    name = doc('#jianjie > div.ks_jj_con > div.doctor_message > div > dl > dt > span').text()
    title = doc('#jianjie > div.ks_jj_con > div.doctor_message > div > dl > dd:nth-child(2)').text().strip('职称：')
    department = doc('div.department_l > p > a.pic-name').text()
    special = doc('div.doctor_message > div > dl > dd:nth-child(5)').text().strip('专业特长：')
    resume = doc('#Descri div').text().strip()
    outpatient_info = doc('div.doctor_message > div > dl > dd:nth-child(4) > span').text()
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
    links = doc('#team > ul > li > div > a.doc_name').items()
    for item in links:
        link = 'http://www.309yy.com' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.309yy.com/Doctors/Main?siteId=300'
    main(url)
