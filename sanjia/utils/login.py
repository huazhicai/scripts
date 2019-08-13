import os

import requests
from lxml import etree
import execjs


class Login(object):
    def __init__(self):
        self.headers = {
            'Referer': 'http://www.114yygh.com/index.htm',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
            'Host': 'www.114yygh.com'
        }
        self.login_url = 'http://www.114yygh.com/account/loginStep1.htm'
        self.post_url = 'http://www.114yygh.com/account/loginStep2.htm'
        self.session = requests.Session()

    def token(self):
        post_data = {
            'mobileNo': '18701943997',
            '/index.htm': '/index.htm'
        }
        response = self.session.post(self.login_url, headers=self.headers, data=post_data)
        selector = etree.HTML(response.text)
        token = selector.xpath('//*[@id="loginStep2_pwd_form"]/input/@value')
        return token

    def password(self):
        with open('/Users/mac/PycharmProjects/shengnei/sanjia/utils/sha1.js', encoding='utf-8') as f:
            strs = f.read()
        ctx = execjs.compile(strs).call('hex_sha1', os.getenv('PASSWORD'))
        return ctx

    def login(self):
        resp = self.token()
        post_data = {
            'token': resp[0],
            'mobileNo': resp[1],
            'smsType': resp[2],
            'loginType': resp[3],
            'redirectUrl': resp[4],
            'password': self.password()
        }
        response = self.session.post(self.post_url, data=post_data, headers=self.headers)
        print(response.is_redirect)
        print(response.text)
        # if response.status_code == 200:
        #     print(response.text)


if __name__ == '__main__':
    login = Login()
    login.login()
