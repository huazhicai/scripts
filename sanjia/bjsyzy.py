"""
北京市顺义区中医医院 肾病科
"""

from sanjia.common import *


def get_json(url):
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
    except requests.ConnectionError as e:
        print('get_json:', repr(e))


def parse_detail(url):
    json = get_json(url)
    for item in json:
        if item.get('ksdh') == '肾病科':
            link = 'http://www.bjsyzy.com' + item.get('url') + '.shtml'
            doc = pq(link, encoding='utf-8')
            resume = doc('div.neirongqu > p').text()
            special = re.search(r'擅长.*?[。|\.]', resume)
            special = special.group() if special else ''

            yield {
                'file': os.path.basename(__file__),
                'hospital': '北京市顺义区中医医院',
                'grade': '三甲',
                'name': item['name'],
                'title': item['yszc'],
                'department': item['ksdh'],
                'special': special,
                'resume': resume,
                'outpatient_info': item['czsj'],
                'link': link
            }


def main(url):
    for item in parse_detail(url):
        # print(item)
        save_to_mongo(item)


if __name__ == '__main__':
    url = 'http://www.bjsyzy.com/sitefiles/syyy_zh/xml/jyzn/zjandmy/zjandmy.json'
    main(url)
