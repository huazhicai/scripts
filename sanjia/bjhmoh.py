"""
北京医院 肾脏内科
"""


from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京医院"
    name = doc('dl.person dd p:nth-child(1)').text().strip('姓　　名：')
    title = doc('dl.person dd p:nth-child(4)').text().strip('职\u3000\u3000称：')
    department = doc('dl.person dd p:nth-child(3)').text().strip('科\u3000\u3000室：')
    resume = doc('div.intro p').text().strip()
    special = re.search(r'专长.*。', resume)
    special = special.group() if special else ''
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
    doc = pq(url)
    links = doc('div.all_doctor div.row dl dt a').items()
    for item in links:
        link = 'http://www.bjhmoh.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.bjhmoh.cn/index.php?r=archives/guide/list&id=57&t=1563243894'
    main(url)
