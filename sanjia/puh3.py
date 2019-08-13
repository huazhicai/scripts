"""
北京大学第三医院 肾病内科
"""
from sanjia.common import *


def parse_detail(link):
    doc = pq(link, encoding='gbk')
    items = doc('div[id^="page"]>div.keshi-item').items()
    for item in items:
        file = os.path.abspath(__file__)
        hospital = "北京大学第三医院"
        name = item('dl > dd > h3 > a').text()
        title = item('dl > dd > h3 > span').text()
        department = '肾病内科'

        resume = item('dl > dd > p').text()
        special = re.search(r'擅长.*', resume)
        special = special.group() if special else ''
        # 出诊信息链接地址
        url = 'https://www.puh3.net.cn' + item('#ifrGuestBook').attr('src')
        outpatient_info = parse_outpatient(url)
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
def parse_outpatient(url):
    doc = pq(url)
    week = {1: '周一', 2: '周二', 3: '周三', 4: '周四', 5: '周五', 6: '周六', 7: '周日'}
    outpatient_info = []
    morning = doc('#form1 > div.czsj > table tr:nth-child(2) td').items()
    for a, b in enumerate(morning):
        if b('img'):
            outpatient_info.append(week[a] + '上午 ' + b('img').attr('title'))

    afternoon = doc('#form1 > div.czsj > table tr:nth-child(3) td').items()
    for a, b in enumerate(afternoon):
        if b('img'):
            outpatient_info.append(week[a] + '下午 ' + b('img').attr('title'))

    return outpatient_info


def main(url):
    results = parse_detail(url)
    for result in results:
        collection.update_one({'name': result['name']}, {'$set': result}, True)
        print(result)


if __name__ == '__main__':
    url = 'https://www.puh3.net.cn/sbnk/czxx/index.shtml#'
    main(url)
