"""
北京电力医院 肾脏内科
"""

from urllib.parse import urljoin

from sanjia.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "北京电力医院"
    name = doc('#artibodyTitle > h1').text()
    department = '肾脏内科'
    resume = doc('#artibody_content > p > span').text()
    title = re.search(r'.*?医师', resume).group()
    special = re.search(r'擅长.*?。', resume).group()
    outpatient_info = doc('#zoom > div > dl > dd:nth-child(6) > span').text()
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
    links = doc('div.c_list_content > ul > li > span.c_body_info > a').items()
    for item in links:
        link = urljoin('https://hospital.nc.sgcc.com.cn/pub/hosptail/ksjs/nkxtks/sznk/ysjs/', item.attr('href'))
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'https://hospital.nc.sgcc.com.cn/pub/hosptail/ksjs/nkxtks/sznk/ysjs/index.html'
    main(url)
