"""
北京复兴医院 肾脏内科
"""



from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京复兴医院"
    name = doc('div.main02_left_doctor_01 > h2').text()
    title = doc('div.main02_left_doctor_01 > p:nth-child(4)').text().strip('职称：')
    department = doc('div.main02_left_doctor_01 > p:nth-child(3)').text().strip('科室：')
    special = doc('div.blue_white_block.leader_intro > div > p:nth-child(1)').text().strip('专长：')
    resume = doc('div.blue_white_block.leader_intro > div > div p:not(:nth-last-child(1))').text().strip()
    outpatient_info = doc('div.blue_white_block.leader_intro > div > div > p:nth-last-child(1)').text()
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
        'link': link,
    }


def main(url):
    doc = pq(url)
    links = doc('div.ask_left > div > div:nth-child(3) > ul > li:nth-child(2) > dl > dd > a').items()
    for item in links:
        link = 'https://www.bj-fxh.com' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'https://www.bj-fxh.com/Html/Departments/Main/SearchIndex_10020005.html#doctor'
    main(url)
