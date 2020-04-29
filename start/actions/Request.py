# # -*- coding: utf-8 -*-
import json
import time

from runtime.Action import Action
# from fake_useragent import UserAgent
import requests
import aiohttp
import asyncio


class GetRequestPro(Action):
    """具有‘阿布云’代理ip接口"""
    _id = 'ded1fcae-e968-11e9-8c95-8cec4bd887f3'
    node_info = {"args": [['url_str', 'String', 'ce69b238-f3a7-11e9-b6bb-8cec4bd887f3'],
                          ['charset_str', 'String', 'ce69b239-f3a7-11e9-bdb8-8cec4bd887f3'],
                          ['proxyuser_str', 'String', 'ce69b23a-f3a7-11e9-aef4-8cec4bd887f3'],
                          ['proxyPass_str', 'String', 'ce69b23b-f3a7-11e9-b28b-8cec4bd887f3'],
                          ['In', 'Event', 'ce69b23c-f3a7-11e9-8df4-8cec4bd887f3']],
                 "returns": [['response_str', 'String', 'ce69b23d-f3a7-11e9-a396-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b23e-f3a7-11e9-a069-8cec4bd887f3']]}

    def __call__(self, args, io):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        url = args['url_str']
        Charset = args['charset_str']
        # 要访问的目标页面
        targetUrl = url
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"
        # 代理隧道验证信息
        proxyUser = args['proxyuser_str']
        proxyPass = args['proxyPass_str']
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        if proxyHost and proxyPass:
            proxies = proxies
        # else:
        #     proxies = None
        re = requests.get(targetUrl, headers=headers, proxies=proxies)
        if Charset: re.encoding = Charset
        content = re.text
        if re.status_code == 200:
            io.set_output('response_str', content)
            io.push_event('Out')
        else:
            self.__call__(args, io)


NETWORK_STATUS = True


class GetRequest(Action):
    '''get请求节点，默认五次请求，最大连接时长Timeout=20'''
    """
    发送get请求，根据response_type返回数据类型内容;
    retry: 默认重新请求5次
    """
    _id = 'ba59b054-10f3-11ea-bf3f-8cec4bd887f3'
    node_info = {"args": [['url_str', 'String', 'baf36bd0-10f3-11ea-a789-8cec4bd887f3'],

                          ['headers', 'String', 'ca7d328a-10f3-11ea-9e81-8cec4bd887f3'],

                          ['In', 'Event', 'cb510dae-10f3-11ea-9de8-8cec4bd887f3']],
                 "returns": [['response', 'String', 'dd881026-10f3-11ea-8d84-8cec4bd887f3'],
                             ['Out', 'Event', 'de035168-10f3-11ea-b799-8cec4bd887f3']]}

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Connection': 'close'}

    def pase(self, url):
        try:
            response = requests.get(url=url, headers=self.headers, verify=False, timeout=(1, 7))
            if response.status_code == 200:
                return response.text
        except requests.exceptions.Timeout:
            global NETWORK_STATUS
            NETWORK_STATUS = False  # 请求超时改变状态
            if NETWORK_STATUS == False:
                '''请求超时'''
                for i in range(1, 5):
                    try:
                        print('请求超时，第%s次重复请求,请求url：%s' % (i, url))
                        if i > 2:
                            response = requests.get(url=url, headers=self.headers, verify=False, timeout=(20, 15))
                            if response.status_code == 200:
                                return response.text
                        else:
                            response = requests.get(url=url, headers=self.headers, verify=False, timeout=(2, 7))
                            if response.status_code == 200:
                                return response.text
                    except requests.exceptions.Timeout:
                        if i == 4: self.pase(url)
                        time.sleep(1)
                        continue

    def __call__(self, args, io):
        url = args['url_str']
        headers = args['headers']
        if headers:
            self.headers = headers
        content = self.pase(url)
        if content:
            io.set_output('response', content)
            io.push_event('Out')


class PostRequest(Action):
    """发送post请求，根据response_type 返回数据类型"""
    _id = '507c4cde-10f4-11ea-b977-8cec4bd887f3'
    node_info = {"args": [['url_str', 'String', '50df5792-10f4-11ea-a522-8cec4bd887f3'],
                          ['data_dict', 'Dict', '513bdcb8-10f4-11ea-b2af-8cec4bd887f3'],
                          ['charset_optional_str', 'String', '5d718a46-10f4-11ea-a06d-8cec4bd887f3'],
                          ['cookie_optional_dict', 'Dict', '5dbf74fa-10f4-11ea-8e6d-8cec4bd887f3'],
                          ['responseType_optional_str', 'String', '5dec9388-10f4-11ea-93f0-8cec4bd887f3'],
                          ['In', 'Event', '6e02c34c-10f4-11ea-93d0-8cec4bd887f3']],
                 "returns": [['response', 'String', '6e6e3534-10f4-11ea-9724-8cec4bd887f3'],
                             ['Out', 'Event', '6ec41528-10f4-11ea-90cf-8cec4bd887f3']]}

    def __call__(self, args, io):
        url = args['url_str']
        data = args['data_dict']
        charset = args.get('charset_optional_str', None)
        cookies = args.get('cookie_optional_dict', None)
        response_type = args.get('responseType_optional_str')

        headers = {'User-Agent': UserAgent(verify_ssl=False).random,
                   'Connection': 'close'
                   }
        if cookies:
            headers.update(cookies)

        tries = 0
        while tries < 4:
            try:
                response = requests.post(url, headers=headers, data=data, verify=False)
                if charset:
                    response.encoding = charset
                if response_type and response_type.lower().strip() == 'json':
                    resp = response.json()
                elif response_type and response_type.lower().strip().startswith('byte'):
                    resp = response.content
                else:
                    resp = response.text
                if response.status_code == 200:
                    io.set_output('response', resp)
                    io.push_event('Out')
                break
            except requests.RequestException as e:
                tries += 1
                print('post failed {}: {}'.format(tries, e))


class CoroutinesRequests(Action):
    """通过gevent协程发送requests请求"""
    _id = '19acd034-e969-11e9-be8d-8cec4bd887f3'
    node_info = {"args": [['url_list', 'List', 'f0ecd910-d5e9-48a4-86d0-9e68ca7e94f0'],
                          ['charset_str', 'String', '0bb2171d-6f14-4cef-b367-259660f0d883'],
                          ['In', 'Event', 'c936029a-9007-4549-a9f4-68410f4bd961']],
                 "returns": [['Content', 'String', '098e1794-c886-4f37-b57c-39af23c81ed1'],
                             ['Out', 'Event', '18cf6666-e302-4e95-9429-c40a13a9298c']]}

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Connection': 'close'}
        self.Charset = ''

    def req(self, url, io):

        headers = self.headers
        # headers['User-Agent'] = UserAgent(verify_ssl=False).chrome
        print(url)
        re = requests.get(url=url, headers=self.headers, verify=False, timeout=(3, 7))
        print('成功')
        # requests.adapters.DEFAULT_RETRIES = 5
        re.encoding = self.Charset
        Content = re.text
        if re.status_code == 200 and len(Content) > 0:

            io.set_output('Content', Content)
            io.push_event('Out')

        else:
            print("未渲染成功")
            self.req(url, io)

    def __call__(self, args, io):
        import gevent
        urls = args['url_list']
        if urls:
            self.Charset = args['charset_str']
            gevent.joinall([gevent.spawn(self.req, url, io, ) for url in urls])


class Asyncop_url(Action):
    '''Aiohttp异步请求节点，默认五次请求，最大连接时长Timeout=20'''
    _id = '1f3c7766-e969-11e9-915c-8cec4bd887f3'
    node_info = {"args": [['url_list', 'List', 'ce69b253-f3a7-11e9-a357-8cec4bd887f3'],
                          ['charset_str', 'String', 'ce69b254-f3a7-11e9-a778-8cec4bd887f3'],
                          ['In', 'Event', 'ce69b255-f3a7-11e9-8433-8cec4bd887f3']],
                 "returns": [['response_str', 'String', 'ce69b256-f3a7-11e9-b5e2-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b257-f3a7-11e9-bfd8-8cec4bd887f3']]}

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'Connection': 'close'
            }

    # async def fetch(self, session, url, charset):
    #     headers = self.headers
    #     headers['User-Agent'] = UserAgent(verify_ssl=False).chrome
    #     try:
    #         async with session.get(url, headers=headers,timeout=2,verify_ssl=False) as response:
    #             response.encoding = charset
    #             return await response.text()
    #     except:
    #         for i in range(1, 5):
    #             try:
    #                 print('请求超时，第%s次重复请求,请求url：%s' % (i, url))
    #                 if i > 2:
    #                     async with session.get(url, headers=headers, timeout=20, verify_ssl=False) as response:
    #                         response.encoding = charset
    #                         return await response.text()
    #                 else:
    #                     async with session.get(url, headers=headers, timeout=2, verify_ssl=False) as response:
    #                         response.encoding = charset
    #                         return await response.text()
    #             except :
    #                 if i == 4:await self.fetch(session, url, charset)
    #                 continue
    # async def main(self, url, charset):
    #     async with aiohttp.ClientSession() as session:
    #         html = await self.fetch(session, url, charset)
    #         return html
    # def __call__(self, args, io):
    #
    #     url_list = args['url_list']
    #     charset = args['charset_str']
    #     if url_list:
    #         tasks = [self.main(url, charset) for url in url_list]
    #         asyncio.set_event_loop(asyncio.new_event_loop())
    #         loop = asyncio.get_event_loop()
    #         con_list = loop.run_until_complete(asyncio.gather(*tasks))
    #         loop.close()
    #         for content in con_list:
    #             io.set_output('response_str', content)
    #             io.push_event('Out')


class GetRequestPro_Aiohttp(Action):
    """具有‘阿布云’代理ip接口,通过Aiohttp请求方式"""

    _id = 'f1a820e8-10f4-11ea-9088-8cec4bd887f3'
    node_info = {"args": [['url_str', 'String', '36a96dcc-10f5-11ea-979a-8cec4bd887f3'],
                          ['In', 'Event', '3713fbd0-10f5-11ea-97e3-8cec4bd887f3']],
                 "returns": [['response_str', 'String', '401f4a92-10f5-11ea-9b6e-8cec4bd887f3'],
                             ['Out', 'Event', '40c5c0a8-10f5-11ea-a575-8cec4bd887f3']]}

    def __call__(self, args, io):
        from pyppeteer import launch

        url = args['url_str']
        targetUrl = url
        # 代理服务器
        proxyHost = "http-dyn.abuyun.com"
        proxyPort = "9020"
        # 代理隧道验证信息
        proxyUser = "HX18ZZ42001605OD"
        proxyPass = "F5FAF0A29BC584A3"

        proxyServer = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": proxyUser,
            "pass": proxyPass,
        }
        userAgent = "curl/7.x/line"

        # async def entry():
        #     conn = aiohttp.TCPConnector(verify_ssl=False)
        #     async with aiohttp.ClientSession(headers={"User-Agent": userAgent}, connector=conn) as session:
        #         async with session.get(targetUrl, proxy=proxyServer) as resp:
        #             body = await resp.read()
        #             if resp.status == 200 and len(body) > 0:
        #                 loop = asyncio.get_event_loop()
        #                 loop.run_until_complete(entry())
        #                 loop.run_forever()
        #                 io.set_output('response_str', body)
        #                 io.push_event('Out')
        #             else:
        #                 self.__call__(args, io)


class PyQueryUrl(Action):
    """通过PyQuery发送请求"""
    _id = '8a07ae92-10f5-11ea-a387-8cec4bd887f3'
    node_info = {"args": [['url_str', 'String', '8a9c265a-10f5-11ea-8006-8cec4bd887f3'],
                          ['field_css_dict', 'Dict', '8b05c370-10f5-11ea-b84b-8cec4bd887f3'],
                          ['In', 'Event', '977f5a6e-10f5-11ea-8410-8cec4bd887f3']],
                 "returns": [['doc_str', 'String', '97d39602-10f5-11ea-afe0-8cec4bd887f3'],
                             ['result_dict', 'Dict', '98221100-10f5-11ea-af23-8cec4bd887f3'],
                             ['Out', 'Event', 'a6323690-10f5-11ea-b895-8cec4bd887f3']]}

    def __call__(self, args, io):
        from pyquery import PyQuery
        url = args['url_str']
        doc = PyQuery(url)
        fields = args['field_css_dict']
        result = {}
        for field, (selector, is_list, attr) in fields.items():
            item = doc(selector)
            if is_list:
                item = item.items()
                if attr:
                    result[field] = [ele.attr(attr) for ele in item]
                else:
                    result[field] = [ele.text() for ele in item]
            else:
                if attr:
                    result[field] = item.attr(attr)
                else:
                    result[field] = item.text()
        io.set_output('doc_str', doc)
        io.set_output('result_dict', result)
        io.push_event('Out')


class PyppeteerObject(Action):
    """实例化一个Pyppeteer 的page对象"""
    _id = 'cdc4cbba-eb00-11e9-943e-8cec4bd887f3'
    node_info = {"args": [['executablePath', 'String', 'ce69b262-f3a7-11e9-b716-8cec4bd887f3'],
                          ['In', 'Event', 'ce69b263-f3a7-11e9-a658-8cec4bd887f3']],
                 "returns": [['broswer_str', 'String', 'ce69b264-f3a7-11e9-bc65-8cec4bd887f3'],
                             ['page_str', 'String', 'ce69b265-f3a7-11e9-b383-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b266-f3a7-11e9-a4c0-8cec4bd887f3']]}

    # # autoClose = False,
    # async def createobject(self, io, args):
    #     executablePath = args['executablePath']
    #     broswer = await launch(headless=True, args=['--disable-infobars'], executablePath=executablePath)
    #     io.set_output('broswer_str', broswer)
    #     page = await broswer.newPage()
    #     return page
    #
    # def __call__(self, args, io):
    #     try:
    #         page = asyncio.get_event_loop().run_until_complete(
    #             self.createobject(io, args))
    #         io.set_output('page_str', page)
    #         io.push_event('Out')
    #     except Exception as e:
    #         print(e)


class PyppeteerGoto(Action):
    """通过pyppeteer的page对象模拟打开一个网页"""
    _id = 'd54c3a66-eb00-11e9-b459-8cec4bd887f3'
    node_info = {"args": [['page_str', 'String', 'ce69b267-f3a7-11e9-be08-8cec4bd887f3'],
                          ['login_url', 'String', 'ce69b268-f3a7-11e9-9a33-8cec4bd887f3'],
                          ['In', 'Event', 'ce69b269-f3a7-11e9-b21d-8cec4bd887f3']],
                 "returns": [['page_str', 'String', 'ce69b26a-f3a7-11e9-be26-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b26b-f3a7-11e9-a4c0-8cec4bd887f3']]}

    # async def pagegoto(self, args, io):
    #     page = args['page_str']
    #     login_url = args['login_url']
    #     await page.setUserAgent(UserAgent(verify_ssl=False).random)
    #     await page.goto(login_url)
    #     # await page.waitForNavigation()
    #     # await asyncio.sleep(2)
    #     io.set_output('page_str', page)
    #
    # def __call__(self, args, io):
    #     asyncio.get_event_loop().run_until_complete(
    #         self.pagegoto(args, io))
    #     io.push_event('Out')


class SessionSetcookie(Action):
    _id = '56bacec0-ec08-11e9-b289-8cec4bd887f3'
    node_info = {"args": [['cookies_list', 'List', 'ce69b26c-f3a7-11e9-8ad0-8cec4bd887f3'],
                          ['cookies_dict', 'Dict', 'ebff8f8f-0050-11ea-8ba7-8cec4bd83f9f'],
                          ['In', 'Event', 'ce69b26d-f3a7-11e9-a091-8cec4bd887f3']],
                 "returns": [['ss_str', 'String', 'ce69b26e-f3a7-11e9-b240-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b26f-f3a7-11e9-949a-8cec4bd887f3']]}

    def __call__(self, args, io):
        cookies_list = args['cookies_list']
        cookies_dict = args['cookies_dict']
        import requests
        ss = requests.session()
        if cookies_list:
            for cookie in cookies_list:
                ss.cookies.set(cookie['name'], cookie['value'])
        if cookies_dict:
            for name, value in cookies_dict.items():
                ss.cookies.set(name, value)
        io.set_output('ss_str', ss)
        io.push_event('Out')


class SessionGeturl(Action):
    """通过session会话机制, 对登录后的页面进行访问"""
    _id = '5c7bd658-ec08-11e9-aa5f-8cec4bd887f3'
    node_info = {"args": [['ss_str', 'String', 'ce69b270-f3a7-11e9-a372-8cec4bd887f3'],
                          ['headers_dict', 'Dict', '3a06a246-042b-11ea-8162-8cec4bd887f3'],
                          ['url_str', 'String', 'ce69b271-f3a7-11e9-a910-8cec4bd887f3'],
                          ['data_dict', 'Dict', 'ce69b272-f3a7-11e9-b3b0-8cec4bd887f3'],
                          ['In', 'Event', 'ce69b273-f3a7-11e9-b851-8cec4bd887f3']],
                 "returns": [['ss_str', 'String', 'ce69b274-f3a7-11e9-8b92-8cec4bd887f3'],
                             ['content_str', 'String', 'ce69b275-f3a7-11e9-ad5b-8cec4bd887f3'],
                             ['cookie_dict', 'String', '4c71d274-042c-11ea-a46e-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b276-f3a7-11e9-8ef5-8cec4bd887f3']]}

    def __call__(self, args, io):
        ss = args['ss_str']
        headers = args['headers_dict']
        if headers:
            headers = headers
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        url = args['url_str']
        data = args['data_dict']
        if data:
            response = ss.get(url, headers=headers, params=data)
        else:
            response = ss.get(url, headers=headers)
        content = response.text
        cookie_dict = requests.utils.dict_from_cookiejar(response.cookies)
        io.set_output('cookie_dict', cookie_dict)
        io.set_output('ss_str', ss)
        io.set_output('content_str', content)
        io.push_event('Out')


class SessionPosturl(Action):
    """通过sessionhuihuajizhi，发post请求"""
    _id = 'c4db4bac-ee1e-11e9-8875-8cec4bd887f3'
    node_info = {"args": [['ss_str', 'String', 'ce69b277-f3a7-11e9-834e-8cec4bd887f3'],
                          ['url_str', 'String', 'ce69b278-f3a7-11e9-8889-8cec4bd887f3'],
                          ['headers_dict', 'Dict', 'bc915b46-042c-11ea-85e1-8cec4bd887f3'],
                          ['data_dict', 'Dict', 'ce69b279-f3a7-11e9-a9b5-8cec4bd887f3'],
                          ['payload_dict', 'Dict', 'f03ab946-04f0-11ea-a7c7-8cec4bd887f3'],
                          ['In', 'Event', 'ce69b27a-f3a7-11e9-8ae4-8cec4bd887f3']],
                 "returns": [['cookie_dict', 'Dict', '31cbbb82-fbbc-11e9-b16c-8cec4bd887f3'],
                             ['ss_str', 'String', 'ce69b27b-f3a7-11e9-b2a8-8cec4bd887f3'],
                             ['content_str', 'String', 'ce69b27c-f3a7-11e9-9f62-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b27d-f3a7-11e9-9d30-8cec4bd887f3']]}

    def __call__(self, args, io):
        ss = args['ss_str']
        headers = args['headers_dict']
        url = args['url_str']
        datas = args['data_dict']
        payload = args['payload_dict']
        if headers:
            headers = headers
        else:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
        if payload:
            data = json.dumps(payload)
        else:
            data = datas

        response = ss.post(url, headers=headers, data=data)
        longin_cookie = requests.utils.dict_from_cookiejar(response.cookies)
        io.set_output('cookie_dict', longin_cookie)
        io.set_output('ss_str', ss)
        io.set_output('content_str', response.text)
        io.push_event('Out')
