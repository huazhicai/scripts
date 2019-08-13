"""
中国医科学院望京医院 内分泌肾病科
"""



from sanjia.common import *


def get_detail_url(html):
    doc = pq(url)
    links = doc('').items()
    return links


def parse_detail(link):
    doc = pq(link, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "中国医科学院望京医院"
    name = doc('div.doct_con p:nth-child(1) span').text()
    title = doc('div.doct_con p:nth-child(1)').text().strip(name)
    department = doc('div.doct_con p.szks_list a').text()
    special = None
    resume = doc('div.tab_box p').text()
    outpatient_info = parse_outpatient(doc)
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
    week = {8: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日' }
    outpatient_info = []
    morning = doc('div.PCDisplay table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append(week[a] + '上午' + b('span').text())

    afternoon = doc('div.PCDisplay table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a + 1] + '下午' + b('span').text())

    return outpatient_info


def main(url):
    doc = pq(url)
    links = doc('li.doct_li a.doct_img').items()
    for item in links:
        link = 'http://www.wjhospital.com.cn' + item.attr('href')
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.wjhospital.com.cn/Html/Departments/Main/DoctorTeam_15.html'
    main(url)
