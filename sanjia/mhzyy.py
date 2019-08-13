"""
民航总医院 肾内科
"""
from sanjia.common import *


def parse_detail(url):
    doc = pq(url)
    items = doc('div.scrollDiv table>tbody > tr').items()
    for item in items:
        file = os.path.basename(__file__)
        hospital = "民航总医院"
        name = item('td:nth-child(2) > a').text()
        title = item('td:nth-child(3)').text()
        department = item('td:nth-child(1)').text()
        special = item('td:nth-child(4)').text()
        outpatient_info = item('td:nth-child(5)').text()
        token = item('td:nth-child(2) > a').attr('onclick')
        resp = get_resume(token)
        resume = resp[1]
        url = resp[0]

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
            'link': url
        }


def get_resume(token):
    sult = re.search(r'\(.*?\)', token, re.S).group()
    a = eval(sult)[2]
    b = eval(sult)[3]
    url = 'http://www.mhzyy.cn/servlet/NewsServlet?method=viewNewsList&categoryCode=NEPHROLOGYDOCTOR&N_NEWSUUID={}&N_RELEVANCEOBJUUID={}'.format(
        a, b)
    resp = get_resp(url)
    doc = pq(resp)
    resume = doc('p.MsoNormal span').text()
    return (url, resume)


def main(url):
    results = parse_detail(url)
    for result in results:
        # print(result)
        save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.mhzyy.cn/servlet/SpecialistServlet?method=getSpecialistWithNewsList&SEARCH_LABCODE=NEPHROLOGY&categoryCode=NEPHROLOGYDOCTOR'
    main(url)
