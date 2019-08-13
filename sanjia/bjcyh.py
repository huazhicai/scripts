# 首都医科大学附属北京朝阳医院
# 肾内科科室专家，代号 289
from sanjia.common import *


def parse_detail(url):
    doc = pq(url, encoding='utf-8')
    file = os.path.basename(__file__)
    hospital = "首都医科大学附属北京朝阳医院"
    name = doc('div.doct_con p:nth-child(1) span').text()
    title = doc('div.doct_con p:nth-child(1)').text().strip(name)
    department = doc('div.doct_con p.szks_list').text().strip('科室：')
    special = doc('div.doct_con p.doc_ShanChang').text().strip('擅长：')
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
        'link': url
    }


# 解析出诊信息
def parse_outpatient(doc):
    week = {2: '周一', 3: '周二', 4: '周三', 5: '周四', 6: '周五', 7: '周六', 8: '周日'}
    outpatient_info = []
    morning = doc('div.PCDisplay table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('span'):
            outpatient_info.append(week[a] + '上午')

    afternoon = doc('div.PCDisplay table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('span'):
            outpatient_info.append(week[a + 1] + '下午')

    return outpatient_info


def main(url):
    doc = pq(url)
    detail_links = doc('.doctorList.mt15 .doct_li a.doc_name').items()
    for url in detail_links:
        url = 'https://www.bjcyh.com.cn' + url.attr('href')
        results = parse_detail(url)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'https://www.bjcyh.com.cn/Html/Departments/Main/DoctorTeam_289.html'
    main(url)
