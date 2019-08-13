"""
北京中医药大学东值门医院 肾病内分泌1区
"""

from multiprocessing.pool import Pool

from lxml import etree
from sanjia.common import *


def parse_detail(link):
    html = requests.get(link).text
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "北京中医药大学东值门医院"
    name = doc('div.linkmap>span>a>span.navspan').text()
    title = doc('div.right_list p:nth-last-child(3)').text().strip('职称：')
    department = doc('div.right_list p:nth-last-child(2)').text().strip('科室：') or '肾病内分泌'
    special = doc('div.right_list p:nth-last-child(2)').text().strip('特长：')
    resume = doc('div.main_bottom_left p').text().strip("[详细]") or doc('div.doc_content p').text().strip()
    # resume = doc('div.main_bottom_left > p > a').attr('href')
    outpatient_info = parse_outpatient(etree.HTML(html))
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


# 解析出诊信息
def parse_outpatient(doc):
    week = {1: '周二', 2: '周三', 3: '周四', 4: '周五', 5: '周六', 6: '周日', 7: '周一'}
    outpatient_info = []
    morning = doc.xpath('//*[@id="con_tableb_1"]//tr[2]/td[position()<9]')
    for a, b in enumerate(morning):
        if b.xpath('.//span/text()'):
            outpatient_info.append(week[a] + '上午' + b.xpath('.//span/text()')[-1].strip())

    afternoon = doc.xpath('///*[@id="con_tableb_1"]//tr[3]/td[position()<9]')
    for a, b in enumerate(afternoon):
        if b.xpath('span'):
            outpatient_info.append(week[a] + '下午' + b.xpath('.//span/text()')[-1].strip())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('ul.docteam_list.clearfix li>a').items()
    for item in links:
        link = 'http://www.dzmyy.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    links = ['http://www.dzmyy.com.cn/Html/Departments/Main/DoctorTeam_{}.html'.format(page) for page in [23, 45]]
    pool = Pool()
    pool.map(main, links)
