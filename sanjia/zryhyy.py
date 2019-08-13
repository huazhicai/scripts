"""
中日友好医院 肾病科
"""



from sanjia.utils.common import *


def get_detail_url(html):
    doc = pq(url)
    links = doc('ul.docteam_list.clearfix li a.doc_name').items()
    return links


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "中日友好医院"
    name = doc('ul.files li a.doc_name').text()
    title = doc('ul.files li:nth-child(2) span').text()
    department = doc('ul.files li:nth-child(3) span').text()
    special = doc('div.doc_intro p').text()
    resume = doc('div.doc_index_right1.otherdocmar').text().strip() or doc('div.doc_index_right1').text().strip()
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
    week = {6: '周四', 7: '周五', 8: '周六', 2: '周日', 3: '周一', 4: '周二', 5: '周三'}
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
    links = doc('').items()
    for item in links:
        link = 'https://www.zryhyy.com.cn' + item.attr('href')
        # print(link)

        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'https://www.zryhyy.com.cn/Html/Departments/Main/DoctorTeam_33.html'
    main(url)
