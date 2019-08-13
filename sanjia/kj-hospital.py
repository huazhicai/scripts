"""
空军总医院 肾脏内科
"""

from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "空军总医院"
    name_title = doc(
        '#__01 > tr > td:nth-child(4) > table > tr > td > table > tr:nth-child(7) > td > table > tr:nth-child(2) > td > table > tr:nth-child(2) > td > table > tr > td > b').text()
    name = name_title.split('：')[1]
    title = name_title.split('：')[0]
    department = '风湿肾病科'
    resume = doc(
        '#__01 > tr > td:nth-child(4) > table > tr > td > table > tr:nth-child(7) > td > table > tr:nth-child(2) > td > table > tr:nth-child(2) > td > table > tr > td').text().strip(
        name_title).strip()
    special = re.search(r'[擅长|熟练].*?。', resume)
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
    links = doc(
        '#__01 > tr > td:nth-child(4) > table  > tr > td > table  > tr:nth-child(6) > td > table > tr > td > table > tr > td > a').items()
    for item in links:
        link = 'http://www.kj-hospital.com/' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.kj-hospital.com/zj.asp?id=212&zjid=2620'
    main(url)
