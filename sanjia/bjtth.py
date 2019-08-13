"""
北京天坛医院 肾脏内科
"""
from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, headers=headers, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京天坛医院"
    name = doc('#summary > div > div.doct_con > p:nth-child(1) > span').text()
    title = doc('#summary > div > div.doct_con > p:nth-child(1)').text().strip(name)
    department = doc('#summary > div > div.doct_con > p.szks_list > a > span').text()
    special = doc('#summary > div > div.doct_con > p.doc_sc').text().strip('擅长：')
    resume = doc('div.tab_box p').text().strip()
    outpatient_info = []
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
    doc = pq(url, headers=headers)
    links = doc('li.doct_li a.doct_img').items()
    for item in links:
        link = 'http://www.bjtth.org' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.bjtth.org/Html/Departments/Main/DoctorTeam_1078.html'
    main(url)
