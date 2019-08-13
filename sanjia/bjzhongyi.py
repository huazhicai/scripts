"""
北京中医医院 肾病科
"""

from sanjia.utils.common import *
from lxml import etree 


def parse_detail(link):
    html = get_resp(link)
    doc = etree.HTML(html)
    file = os.path.basename(__file__)
    hospital = "北京中医医院"
    name = doc.xpath('/html/body/div/div[1]/div[2]/div[2]/h1/text()')[0]
    resume = ','.join(doc.xpath('/html/body/div/div[1]/div[2]/div[2]/div[2]//text()')).strip()
    title = re.search(r'.{2,3}医师', resume).group()
    department = '肾病科'
    special = re.search(r'擅.*?。', resume)
    special = special.group() if special else ''
    outpatient_info = re.findall(r'出诊时间：.*', resume)
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
    links = doc('div.kszj_content > div > dl > dd > ul > a').items()
    for item in links:
        link = 'http://www.bjzhongyi.com' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.bjzhongyi.com/departments/article/355.html'
    main(url)
