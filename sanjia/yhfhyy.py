"""
北京燕化医院 肾病内科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京燕化医院"
    name = doc('div.linkmap > span > a:nth-child(5) > span').text()
    title = doc('div.doctor_con > dl > dd:nth-child(2)').text().strip('职称：')
    department = "肾内科"
    special = doc('div.doctor_con > dl > dd:nth-child(6)').text().strip('专长：')
    resume = doc('div.doctor_con > dl > dd:nth-child(5) > p').text().strip() or doc('#zoom > p:nth-child(1)').text()
    outpatient_info = doc('div.doctor_con > dl > dd:nth-child(7) > span').text()
    special = re.search(r'擅长.*。', resume).group() if not special else special
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


def main(url):
    doc = pq(url)
    links = doc('div.doc_td ul li a.doc_name').items()
    for item in links:
        link = 'http://www.yhfhyy.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.yhfhyy.com.cn/Html/Doctors/Main/Index_292.html'
    main(url)
