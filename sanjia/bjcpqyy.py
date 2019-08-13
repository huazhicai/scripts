"""
昌平区医院 肾脏内科
"""


from sanjia.utils.common import *


def parse_detail(link):
    doc = pq(link)
    file = os.path.basename(__file__)
    hospital = "昌平区医院"
    resume = doc('#FrontProducts_detail02-1503458643405_cont_1 > p:nth-child(3)').text().strip()
    name = re.search(r'(.*?),', resume).group(1)
    title = re.search(r'([副|主].*?医师)', resume).group(1)
    department = '肾内科'
    special = re.search(r'专业特长(.*。)', resume).group(1)
    outpatient_info = doc('#FrontProducts_detail02-1503458643405_cont_1 > p:nth-child(4)').text().strip('出诊时间：')
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
    links = doc('#FrontProducts_list01-1503454347592 > ul > li > div.pic-module > div > a').items()
    for item in links:
        link = 'http://www.bjcpqyy.com.cn' + item.attr('href')
        # print(link)
        results = parse_detail(link)
        for result in results:
            # print(result)
            save_to_mongo(result)


if __name__ == '__main__':
    url = 'http://www.bjcpqyy.com.cn/zjjs/searchType=productFilterSearch&brandId=&key15=&key14=&key13=&key12=16&key19=&key18=&key17=&key16=&pmcId=48&spec5=&spec6=&spec3=&spec4=&spec9=&spec7=&spec8=&key10=&key11=&spec1=&spec2=&spec0=&method=submit.html'
    main(url)
