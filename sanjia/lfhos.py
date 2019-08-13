"""
北京市隆福医院 肾病科
"""
from sanjia.utils.common import *
from lxml import etree


def parse_detail(link):
    html = get_resp(link)
    doc = etree.HTML(html)
    file = os.path.basename(__file__)
    hospital = "北京市隆福医院"
    resp = doc.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/p[1]/span/text()')
    if resp and '肾' in resp[0]:
        name = resp[1].split('\xa0')[0].strip()
        title = resp[1].split('\xa0')[1].strip()
        department = resp[0]
        special = doc.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/p[2]/span/text()')[0].strip()
        resume = doc.xpath('//*[@id="form1"]/div[6]/div[2]/div[2]/p[2]/span/text()')[1].strip()
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


if __name__ == '__main__':
    for nsid in range(408, 454):
        url = 'http://www.lfhos.com/web/exportSingle.aspx?nsid={nsid}'.format(nsid=nsid)
        # resp = get_resp(url)
        results = parse_detail(url)
        for result in results:
            # print(result)
            save_to_mongo(result)
