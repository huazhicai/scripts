"""
北京清华长庚医院 肾病科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京清华长庚医院"
    name = doc('div.touxiang > div > h5').text().strip('姓名：')
    title = doc('div.touxiang > div > p:nth-child(2)').text().strip('职务：')
    department = '肾脏内科'
    special = doc('div.touxiang > div > p:nth-child(3)').text().strip('特长：')
    resume = doc('div.jybj').text().strip()
    outpatient_info = []
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
    links = doc('div.academic > ul > li > a').items()
    for item in links:
        link = 'http://www.btch.edu.cn/ksdh/nkb/sznk/ysjs_sznk/' + item.attr('href')
        print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.btch.edu.cn/ksdh/nkb/sznk/ysjs_sznk/index.htm'
    main(url)
