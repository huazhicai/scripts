# -*- coding: utf-8 -*-
import requests
from runtime.Action import Action
from datetime import datetime, timedelta
import re
from lxml import html, etree
import pymssql
from multiprocessing.pool import Pool


class HuayanSystem(Action):
    _id = '9ed37096-bc78-47c9-b0d0-663259856122d'
    node_info = {"args": [['patientId', 'Int', 'e142135d-e9a4-11e9-9dd5-f4523145acec'],
                          ['In', 'Event', 'e76325ad0-e9a4-11e9-bc41-f432541254ec']
                          ],
                 "returns": [['huayan_array', 'List', 'e7523af31-e9a4-11e9-bb0d-f416630aacec'],
                             ['Out', 'Event', 'e7102f42-e9a4-11e9-ba9b-f6325a27acec']]}

    def __init__(self):
        self.host = 'http://192.168.50.217:8088'

    def get_requeest(self, url):
        resp = requests.get(url)
        return resp.json()

    def split_href(self, raw):
        ret = re.search(r'\d{4}-\d{1,2}-\d{1,2}', raw)
        if ret:
            return ret.group()

    def get_ktv(self, patient_id):
        """
        web网页字段对应的id
        {
            'touxiqianniaosu': 300,
            'zhiliaohoutianshu': 652,
            'tizhong': 304,
            'ktv'： 308,
            'jianchariqi'： 307，
            'touxihouniaosu': 301,
            'touxishijian': 302
            'tuoshuiliang' 303,
        }
        """
        url = self.host + '/assay/listData/{}/21'.format(patient_id)
        resp = self.get_requeest(url)
        ktv_s = []
        p = lambda x, y: x[y].replace('&nbsp;', '')
        for i in resp['data']:
            ktv_s.append({
                13004: p(i, '300'),
                13002: p(i, '652'),
                13008: p(i, '304'),
                13003: p(i, '308'),
                13001: self.split_href(i['307']),
                13005: p(i, '301'),
                13006: p(i, '302'),
                13007: p(i, '303'),
            })
        return ktv_s

    def get_urr(self, patient_id):
        """
        肾功能菜单下
        """
        url = self.host + '/assay/listData/{}/19'.format(patient_id)
        resp = self.get_requeest(url)
        urr_s = []
        p = lambda x, y: x[y].replace('&nbsp;', '')
        for i in resp['data']:
            urr_s.append({
                13108: p(i, '295'),
                13104: p(i, '289'),
                13107: p(i, '294'),
                13105: p(i, '292'),
                13101: self.split_href(i['323']),
                13103: p(i, '465'),
                13106: p(i, '293'),
                13109: p(i, '463'),
                13102: p(i, '651'),
            })
        return urr_s

    def get_npcr(self, patient_id):
        url = self.host + '/assay/listData/{}/36'.format(patient_id)
        resp = self.get_requeest(url)
        npcr_s = []
        p = lambda x, y: x[y].replace('&nbsp;', '')
        for i in resp['data']:
            npcr_s.append({
                13205: p(i, '538'),
                13203: p(i, '542'),
                13208: p(i, '541'),
                13210: p(i, '678'),
                13204: p(i, '537'),
                13209: p(i, '679'),
                13201: self.split_href(i['536']),
                13207: p(i, '540'),
                13202: p(i, '661'),
                13206: p(i, '539'),
            })
        return npcr_s

    def get_ztdbbhd(self, patient_id):
        """
        铁五项
        """
        url = self.host + '/assay/listData/{}/8'.format(patient_id)
        resp = self.get_requeest(url)
        ztdbbhd_s = []
        p = lambda x, y: x[y].replace('&nbsp;', '')
        for i in resp['data']:
            ztdbbhd_s.append({
                13303: p(i, '187'),
                13307: p(i, '188'),
                13306: p(i, '186'),
                13301: self.split_href(i['252']),
                13304: p(i, '184'),
                13305: p(i, '185'),
                13302: p(i, '644'),
            })
        return ztdbbhd_s

    def __call__(self, args, io):
        patient_id = args['patientId']
        result = {
            'ktv': self.get_ktv(patient_id),
            'urr': self.get_urr(patient_id),
            'npcr': self.get_npcr(patient_id),
            'ztdbbhd': self.get_ztdbbhd(patient_id),
        }
        io.set_output('huayan_array', [result])
        io.push_event('Out')


class HisSystem(Action):
    _id = '9ed37096-bc78-47c9-b0d0-654fef1f8122d'
    node_info = {"args": [['Name', 'String', 'e1460f3d-e9a4-11e9-9dd5-f416630aacec'],
                          ['Binglihao', 'String', 'e3250f3d-e9a4-11e9-9dd5-f416630aacec'],
                          ['In', 'Event', 'e7260f40-e9a4-11e9-bc41-f416631254ec']
                          ],
                 "returns": [['Array', 'List', 'e72601231-e9a4-11e9-bb0d-f416630aacec'],
                             ['Out', 'Event', 'e7102f42-e9a4-11e9-ba9b-f416630aacec']]}

    def __init__(self):
        self.host = 'http://192.168.17.102'
        self.user = '7468'
        self.passwd = '7468'
        self.session = requests.Session()

    def login(self):
        url = self.host + '/zwemr/Main/Login.aspx'
        check_url = self.host + '/zwemr4/Query/ZHCXLogin.aspx?gh={}'.format(self.user)
        post_data = {
            "__VIEWSTATE": "/wEPDwUIOTY5MTM3MDFkGAEFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYBBQhpYnRMb2dpbo70erIjrWYl11BY/WrM1yrv03xJ",
            "__EVENTVALIDATION": "/wEWCAKRuMWQCgK57dLhAQLgr6WJAwKM2r7XBwLisayFDQKu7NfcDQLX69fcDQKr8tnHBv/B8UGeIXik+Srwu1iIRDae5MHM",
            "tbID": self.user,
            "tbPWD": self.passwd,
            'ddlVersion': '新版本',
            "hdBasicRole": "5",
            "select": "5",
            'hdWordID': '',
            'ibtLogin.y': '0',
            'ibtLogin.x': '0',
        }
        resp = self.session.post(url, data=post_data)
        res = self.session.get(check_url)

    def chaxun_request(self, key, year):
        url = self.host + '/zwemr4/Query/BrcryDj.aspx?gh={}'.format(self.user)
        post_data = {
            "__VIEWSTATE": "/wEPDwULLTEzNzUyMDQwMDkPZBYCZg9kFgICAw9kFgQCAQ9kFgJmDw8WAh4HVmlzaWJsZWhkFgICAQ8WAh4EVGV4dGVkAgMPZBYIAgEPZBYEAgEPEA8WBh4ORGF0YVZhbHVlRmllbGQFBGJxaWQeDURhdGFUZXh0RmllbGQFBmJxbmFtZR4LXyFEYXRhQm91bmRnZBAVsAEM5omA5pyJ55eF5Yy6DULotoXlvanotoXlrqQJ55eF55CG56eRDkNDVeeXheaIvyg1LTMpHeWmh+S6p+enkSjkuqfnp5Ep55eF5oi/KDUtM0EpEui2heWjsOS7i+WFpeeXheaIvxrln47nq5nlpofkuqfnp5Hnl4XmiL8oMS00KR3ln47nq5nlubLpg6jkv53lgaXnl4XmiL8oMi0zKRfln47nq5nogpvogqDnl4XmiL8oMi0xKSDln47nq5nogpvogqDlpJbnp5Hkuoznl4XljLooNS00KRfln47nq5nogp3ngo7nl4XmiL8oMS0xKRfln47nq5nljJbnlpfnl4XmiL8oMy0xKRTln47nq5lJQ1Xnl4XmiL8oNS0yKR3ln47nq5nnsr7npZ7ljavnlJ/nl4XmiL8oMy00KSDln47nq5nmgKXor4rlhajnp5Hkuoznl4XljLooMS00KRfln47nq5nogIHlubTnl4Xnp5EoMi0zKRHln47nq5npurvphokoNS00KRfln47nq5nlhoXkuoznl4XljLooMy0yKRfln47nq5nlhoXkuIDnl4XljLooMy0yKRfln47nq5nnmq7ogqTnl4XmiL8oNS0zKR3ln47nq5nogr7nl4XpgI/mnpDnl4XljLooMS0xKSDln47nq5nnpZ7nu4/lhoXnp5HkuIDnl4XljLooNS0zKRTln47nq5nmiYvmnK/lrqQoNS00KR3ln47nq5nog4PogqDlpJbnp5Hnl4XmiL8oNS0yKRrln47nq5nooYDmtrLnl4Xnl4XmiL8oMi00KSXln47nq5nooYDmtrLnl4Xnl4XmiL8oTURT5Lit5b+DKSgxLTMpGuWfjuermeihgOa2sueXheeXheaIvygzLTMpHeWfjuermeihgOa2sumrmOe6p+eXheWMuigyLTIpIOWfjuermeihgOa2sumrmOe6p+S6jOeXheWMuigxLTMpGuWfjuermeecvOenkeS6jOeXheWMuigxLTIpGuWfjuermeecvOenkeS4gOeXheWMuigxLTEpHeWfjuermee7vOWQiOW6t+WkjeeXheWMuigxLTEpHeWfjuermeiCv+eYpOWGheenkeeXheaIvyg2LTMpHeWfjuermeiCv+eYpOWkluenkeeXheaIvyg1LTQpFeWfjuermemHjeeXh+ebkeaKpOWupBrogLPpvLvlkr3llonnp5Hnl4XmiL8oMy02KRLlhL/np5Hnl4XmiL8oNS0yQSkc5aaH5Lqn56eRKOWmh+enkSnnl4XmiL8oNS0zKRLlpofnp5Hnl4XmiL8oNS0zQSkW5pS+55aX56eR55eF5oi/KDZCLTEwKQzlj5Hng63nl4XljLoY6aOO5rm/5YWN55ar55eF5oi/KDItMTkpD+aUvuWwhOWvvOeuoeWupBLohbnpgI/nl4XmiL8oNkItOSkR6LSf5Y6L55eF5oi/KDktNSkW6IK656e75qSN55eF5Yy6KDZCLTIwKRbogrrnp7vmpI3nl4XljLooNkItMTkpGeiDuOmDqOiCv+eYpOeXheaIvyg2Qi0xOSkc5bmy6YOo55eF5oi/5LiA55eF5Yy6KDZCLTIyKRzlubLpg6jnl4XmiL/kuoznl4XljLooNkItMjMpHOW5sumDqOeXheaIv+S4gOeXheWMuig2Qi0yMSkX6IKb6IKg5aSW56eR55eF5oi/KDUtMSkY6IKb6IKg5aSW56eR55eF5oi/KDUtMUEpJeiCneiDhuiDsOWkluenkeS4reW/g+S5neeXheWMuig2Qi0xOCkm6IKd6IOG6IOw5aSW56eR5Lit5b+D5LiA55eF5Yy6KDZCLTEyQSkl6IKd6IOG6IOw5aSW56eR5Lit5b+D5LqM55eF5Yy6KDZCLTEzKSXogp3og4bog7DlpJbnp5HkuK3lv4Plha3nl4XljLooNkItMTUpJeiCneiDhuiDsOWkluenkeS4reW/g+S4ieeXheWMuig2QS0xMykl6IKd6IOG6IOw5aSW56eR5Lit5b+D5YWr55eF5Yy6KDZCLTE3KSXogp3og4bog7DlpJbnp5HkuK3lv4Plm5vnl4XljLooNkEtMTQpJeiCneiDhuiDsOWkluenkeS4reW/g+S6lOeXheWMuig2Qi0xNCkl6IKd6IOG6IOw5aSW56eR5Lit5b+D5LiD55eF5Yy6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MgcxMDQxMTEyBzEyMDAxMjMHMTE2MDgwMgcxMDMxNDEyBzEwMzExMTAHMTE1MDIxMgcxMjAwMTI0BzEwMTAyMTMHMTI2MDExMQcxMDMxODAwBzEwMzE5MDAHMTEzMDExMgcxMDQxMDE2BzEwMzAzMTMHMTU0MDIxMQcxMDQwMTI1BzEwMzA1MTIHMTAzMDUwOQcxMDMwNTEzBzEwMzA1MTEHMTAzMDUxNwcxMTAwMTEyBzExMDAxMTMHMTAzMjMwMAcxMDMxNDE0BzExOTAxMTIHMTAzMTExMwcxMTEwMTAyBzEwNzAxMDMHMTA1MDEwMgcxMDUwMTAzBzEwMzIwMDIHMTE2MDcwNgcxMDMwODAyBzEzMjAxMDUHMTA0MTAxMwcxMTYxMTAxBzEwNDE2MDMHMTA0MTYwMQcxMDMyMjAxBzEwMTAyMDMHMTAxMDIwNAcxMDEwMjAyBzEwNDExMDIHMTA0MTEwNAcxMDQwMTE3BzEwNDAxMzAHMTA0MDExMAcxMDQwMTA1BzEwNDAxMzEHMTA0MDEzNQcxMDQwMTMyBzEwNDAxMzMHMTA0MDEzNAcxMDEwMzA1BzEwMTAzMDEHMTAxMDQwMgcxMDQwMzAzBzEwNDAzMDIHMTE2MDcwMgcxMTYwMzAzBzExNjAzMDIHMTE2MDkwMQcxMTYwOTA3BzExNjA5MDYHMTE2MDkwNAcxMTYxMDAxBzExNjEyMDEHMTAzMDUxOAcxMDMwNTE1BzEwMzE1MDAHMTAzMTQwMQcxMDMwMTA2BzEwMzAxMDIHMTAzMDEwNwcxMzIwNDA0BzEwMzExMDIHMTMyMDEwNAcxMTUwMjAyBzEwMTAzMDIHMTIwMDEwMwcxMjAwMTAxBzEyMDAxMjUHMTIwMDEwMgcxMDQwMTA5BzEwNDAxNDAHMTIxMDEwMgcxMTIwMjAyBzE1NTAzMDEHMTAxMDIwNQcxMDEwMjA2BzEwMTAyMDcHMTA0MDEzNwcxMDQwNDA0BzEwNDA0MDYHMTA0MDQxMQcxMDQwNDEzBzEwNDA0MTAHMTA0MDQwMwcxMDQwNDEyBzEwNDA0MTUHMTA0MDQyMwcxMjYwMTAwBzEwMzA3MDIHMTAzMDAwMwcxMzIwNDA2BzExMzAxMDIHMTE2MDcwNAcxMDQwNTE1BzEwNDA1MDQHMTA0MDUxMAcxMDMxNjAxBzEw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",
            "_ctl0:C1:TxtRyStartDate": '{}-01-01'.format(year),
            "_ctl0:C1:TxtRyEndDate": '{}-12-31'.format(year),
            "_ctl0:C1:ddlSex": "0",
            "_ctl0:C1:BtnQuery": "\u67e5\u8be2",
            "_ctl0:C1:ddlLjbr": "0",
            "__EVENTVALIDATION": "/wEW2QECnL7k7QcCubDN5QMC76rtpg4C0dra6AwCw8OQhQsCgvGrigECjZOkpgMCg/GnigECjaihggkC3aWYyQcCqo/v6AMChOrF3QgCqe2ykAEC5rqJrg0CmeiNsgsCo/36kgECoJ+DtwMCksGnxgIC77qNrg0C7rqNrg0CrO3K1gECzsCQsggCxcO4xQsCj+HrwAEC8JzysgoCqO3e0wECodvpxQYCz8O4xQsC+ZH3EwKz/7OuDALB5bGTBgKqj9fpAwLYuuHuDALX1YGTBgKCj5TDBwLDw6yFCwKKqKmBCQLfg5/2BQKm6IW/CwK93+egDQKt7apQAonPsukHArXtwtMBAuq8xrwJAsfOv6QNApLBm4cCAsXOo6QNAovh54kBAvyRw5MHAqCfh7cDAu+/1oIEAo2opYIJAt2lnMkHApfz2OcDAqrqwsgGAqPY0fILAqPY6fILAvCcirIKAozh98kBAvCcjrIKAt2lrAkCxs6z5A0Cl/PopwwChZawtA4C6bHLmAcCl6ilggkCuM/P5w0C36WoCQL96sXdCALa8+uoBgLx6sXdCAKawafHAgL82NDHDQKTz7LpBwLNnImHDAKTwZuHAgKVwZuHAgKK5IvQDALtzI/ECALiuo2uDQKGke/TBwKQiNWECgKs7cLTAQK3/7euDAKKk6CmAwKs7baQAQKBk6CmAwKZ6ImyCwKMqKWCCQKqj9foAwLwoZvSBwKMhpjpDgLB5bGSBgK0q+AzAqPY3fILAoqorYAJAuKq5aAOAoXxn40BAoKWsLQOApmNklkCvOSMwgoCqurKyAYCkPPkpwwCysCg8ggCieGPyQECw87L5w0CrNjp8gsCw87P5w0C5qWkCQL9nIayCgLDzrfkDQKpuITrBAKq7cLTAQLAw7zFCwLQxeWLBwKs7cbWAQLDnImHDAL8nIayCgKT8+SnDAKv2OnyCwL4ke/TBwKK4eeJAQLbpZzJBwKM4ePJAQLLgcakCgK1q9TzBwLHzqOkDQKr6rqJBgKg2N2yCwLM1ZHTBgKu7cLTAQLcpagJAvOcirIKApbz5KcMAqLY7fILApXh54kBAqLYwfULAtylnMkHAvGc/vIJAtqlmMkHAt2lmAkCwcCk8ggCs/+3rgwC3aWkCQLhzOeECAKs7bKQAQLqzPPECAKq6sbIBgKv7cLTAQKr7baQAQKW0cOCAgKp7cLTAQKdiNWECgLZpagJAsLOz+cNApyI1YQKAqjtwtMBAorkj9AMApTz2OcDArmtpcMDAovkj9AMAuyavZgPAoyGgO4OAsHlzZIGAsTOo6QNAtm6ja4NApeY6f4JAsrVhZMGAoKPkMMHAu6Ytt4NAvmcirIKAuKlqAkCweW9lwYC5rqB7A0ClJjVuAkCkJjVuAkCiZjVuAkCpuSZhQ8CptWA5QEC/u6O8QYCmd7LkAUCht7LkAUCh97LkAUC0Mn3+gsCz8n3+gsCzsn3+gsC0YfQ9QYC14jGjQ4Cka7Mlw4Ckum3ggoC3pzNlw4Crdm4ggoCy8GS1QcC/q7k9AYCvs+LGwLM/8iJCAKqw/27DgK1w/GcDgLQi9HQBQKZyPq3BALWzardCAL8r5cQAr6zgtwPAvWYmI4GApSUqbADAvmqi5sJAt7B7YUPAsPYz/AEAqjvsdsKAo2GlEYC8pz2sAYC17PYmwwCvMq6hgICoeGc8QcC+arLgwcC+arf3g8C+arzuQjhjPRc9mBn0ML/LxW1ouSr2G+s+w=="
        }
        if key.isdigit():
            post_data.update({"_ctl0:C1:TxtPid": key, })
            resp = self.session.post(url, data=post_data)
            ret = re.findall(r'LCRecord/EMRFrame.aspx\?zyxh=(\d{8}).*?', resp.text)
            return ret  # 病人索引id列表
        else:
            post_data.update({"_ctl0:C1:TxtPname": key})
            resp = self.session.post(url, data=post_data)
            blh_arry = etree.HTML(resp.text).xpath('//*[@id="_ctl0_C1_GrdCry"]/tr[position()>1]/td[3]/text()')
            return blh_arry

    def zonghechaxun(self, key):
        start_year = 2007
        deadline = datetime.now().strftime('%Y')
        index_ids = []
        while start_year < int(deadline) + 1:
            temp = self.chaxun_request(key, start_year)
            index_ids.extend(temp)
            start_year += 1
        # print(index_ids)
        return index_ids

    def binganshouye(self, idx, blh):
        # self.session.get(self.host+'/zwemr4/LCRecord/EMRFrame.aspx?zyxh={}'.format(idx))
        resp = self.session.get(
            self.host + '/zwemr/Doctors/BingAnShouYeView1.aspx?state=1&zyxh={}&bah={}&gh={}'.format(idx, blh,
                                                                                                    self.user))
        doc = etree.HTML(resp.text)
        p = lambda x: ''.join(doc.xpath('//*[@id="_ctl0_C1_{}"]//text()'.format(x))).strip()
        p_1 = lambda x: ''.join(
            doc.xpath('//*[@id="_ctl0_C1_{}"]/option[@selected="selected"]/text()'.format(x))).strip()
        p_2 = lambda x: ''.join(doc.xpath('//*[@id="_ctl0_C1_{}"]/@value'.format(x))).strip()
        p_3 = lambda x: ''.join(doc.xpath('//*[@id="_ctl0_C1_{}"]/input[@checked="checked"]/@id'.format(x))).strip()
        p_4 = lambda x: ''.join(doc.xpath('//*[@id="_ctl0_C1_{}"]/label[@for="{}"]/text()'.format(x, p_3(x)))).strip()
        # [30119, 30104, 0, 30101, 30110]
        bingan = {
            30101: p('LabName'),
            30102: p('LabSex'),
            30104: blh,
            30110: p('LabCsrq'),
            30178: p('LabAge'),
            30111: p_1('drNation'),
            30116: p_2('TxtCsd'),
            30127: p_1('AreaCtlFirst_ddlProvince') + \
                   p_1('AreaCtlFirst_ddlCity') + p_1('AreaCtlFirst_ddlArea'),
            30117: p_1('drRace'),
            30119: p('LabIDcard'),
            30106: p('LabYlbxzf'),
            30107: p('LabYlfffs'),
            30115: p_1('drCarrear'),
            30118: p_1('drMarriage'),
            30120: p_2('TextBoxXzd'),
            # 30126: p_2('TxtDwdh'),  # 单位电话
            30121: p_2('TxtGzdw'),
            30122: p_2('Txtgzdwdz'),
            30124: p_2('TxtLxrmc1'),
            30180: p_1('ddlLxrgxID1'),
            30125: p_2('TxtLxrdz1'),
            30126: p_2('TxtLxrdh1'),
            30128: p_1('ddlRytj'),
            30129: p('LabRyrq'),
            30133: p('txtRyzd'),
            30182: 3,  # 数据来源
            30131: p('LabCyrq'),
            30130: p('LabZyts'),

            30136: p_2('TxtSswbyy'),
            30138: p_2('TxtBlzd'),
            30139: p_2('TxtBlh'),  # 病理号
            30174: p_4('DroplstXx'),
            30140: p_1('ddlHbsag'),
            30141: p_1('ddlHcvab'),
            30142: p_1('ddlHivab'),
            30143: p_1('ddlMdkt'),
            30144: p_1('ddlCrbbg'),
            30175: p_4('DroplstRh'),
            # 30137: p_2('TxtYwgm'),
            30173: p_1('DroplstLyfs'),
            30176: p_4('RadioSfzry'),
            30177: ''.join(["入院前：", p_2('TxtRyqt'), '天', p_2('TxtRyqh'), '時', p_2('TxtRyqfz'), '分',
                            " 入院后:", p_2('TxtRyht'), '天', p_2('TxtRyhh'), '時', p_2('TxtRyhfz'), '分']),

            30150: p_2('TxtZyf'),
            30151: p_2('TxtCf'),
            30152: p_2('TxtHlf'),
            30153: p_2('TxtXy'),
            30154: p_2('TxtZcy'),
            30155: p_2('TxtZcaoy'),
            30156: p_2('TxtFs'),
            30157: p_2('TxtHy'),
            30158: p_2('TxtSy'),
            30159: p_2('TxtSx'),
            30161: p_2('TxtSs'),
            30162: p_2('TxtJs'),
            30163: p_2('TxtJc'),
            30164: p_2('TxtMzf'),
            30165: p_2('TxtYrf'),
            30166: p_2('TxtPcf'),
            30167: p_2('TxtQt1'),
            30170: p_2('TextBox2'),
            30168: p_2('TxtQt2'),
            30169: p_2('TxtQt3'),
            30171: p_2('TextBox1')
        }

        q = lambda x, y: ''.join(x.xpath(y)).strip()
        chyjl = []
        temp = doc.xpath('//*[@id="_ctl0_C1_diagChuyuan_dlFirst"]/tr[position()>3]')
        flag = True
        for i in temp:
            checked_id = q(i, './td[3]/span/input[@checked="checked"]/@id')
            ruyuanbingqing = q(i, '//label[@for="{}"]/text()'.format(checked_id)) + q(i, './td[3]/span/text()')
            if flag:
                zhdlx = '主要诊断'
                flag = False
            else:
                zhdlx = '其他诊断'
            chyjl.append({
                30181: zhdlx,
                30132: ruyuanbingqing,
                30135: q(i, './td[4]//text()'),
                30134: q(i, './td[2]//text()'),
                30183: 3,
            })

        ssjczjl = []
        table = doc.xpath('//*[@id="_ctl0_C1_GrdSsinfo"]/tr[position()>1]')
        for j in table:
            ssjczjl.append({
                30145: q(j, './td[1]/text()'),
                30146: q(j, './td[2]/text()'),
                30147: q(j, './td[3]/text()'),
                30148: q(j, './td[7]/text()'),
                30149: q(j, './td[8]/text()'),
            })

        bingan.update({'churuyuanjilu': chyjl, 'ssjczjl': ssjczjl})
        return bingan

    def ruyuanjilu(self):  # 个人病史
        url = self.host + '/zwemr/Doctors/InHosRecordWholeView.aspx'
        resp = self.session.get(url)
        if resp.status_code == 200:
            doc = etree.HTML(resp.text)
            p = lambda x: ''.join(doc.xpath('//*[@id="_ctl0_C1_{}"]//text()'.format(x))).strip().replace('\u3000',
                                                                                                         '').replace(
                '\xa0', '')
            gerenbingshi = {30207: p('lbInhosTime'),
                            30201: p('lbChief'),
                            30202: p('lbXianBingshi'),
                            30203: p('lbJIWang'),
                            30204: p('lbGeRen'),
                            30205: p('lbHunYu'),
                            30206: p('lbJia'),
                            }
            if gerenbingshi.get(30201):  # 有数据才返回
                return gerenbingshi

    def changqiyizhu(self, idx, blh):
        resp = self.session.get(
            self.host + '/zwemr/Instructions/Yz_CqYzd.aspx?zyxh={}&bah={}&gh={}'.format(idx, blh, self.user))
        doc = etree.HTML(resp.text)
        items = doc.xpath('//tr[contains(@id, "_trItem")]')
        m = lambda x, y: ''.join(x.xpath(y)).strip()
        fix_time = lambda x: ''.join(['20', x[:8], ' ', x[8:]]) if len(x) > 7 else None
        yizhu = []
        for item in items:
            yizhu.append({
                30301: fix_time(m(item, './td[1]//text()')),
                30302: m(item, './td[2]//text()'),
                30303: fix_time(m(item, './td[5]//text()'))
            })
        return yizhu

    def yongyaojilu(self, idx, blh):
        # (0.5mg)他克莫司(普乐可复)胶囊 0.5毫克*1粒 饭前口服 BID口服 0.25毫克
        # 蔗糖铁针(维乐福) 100毫克/5毫升*1支 W3D1血透用 100毫克
        yizhu = self.changqiyizhu(idx, blh)
        koufu = []
        zhenji = []
        for item in yizhu:
            content = item[30302]
            if '口服' in content:
                jilu = content.split(' ')
                if len(jilu) > 3:
                    koufu.append({
                        30501: item[30301],
                        30502: jilu[0],
                        30503: jilu[1],
                        30504: jilu[-1],
                        30505: re.sub(r'[\u4E00-\u9FA5]', '', jilu[-2]),
                        30506: re.sub(r'[A-Za-z]', '', jilu[-2]),
                        30507: re.sub(r'[0-9]|\.', '', jilu[-1]),
                        30508: 3,
                        30509: item[30303]
                    })

            if '注' in content or '针' in content:
                jilu = content.split(' ')
                if len(jilu) > 3:
                    zhenji.append({
                        30601: item[30301],
                        30602: jilu[0],
                        30603: jilu[1],
                        30604: jilu[-1],
                        30605: re.sub(r'[\u4E00-\u9FA5]', '', jilu[-2]),
                        30606: re.sub(r'[A-Za-z]', '', jilu[-2]),
                        30607: re.sub(r'[0-9]|\.', '', jilu[-1]),
                        30608: 3,
                        30609: item[30303]
                    })
        return koufu, zhenji

    def chaxun_blbg(self, blh):
        # 02217244 02146187
        url = self.host + '/zwemr/Examination/PisRptQuery.aspx?bah={}&gh={}'.format(blh, self.user)
        global a
        a = lambda x, y: ''.join(etree.HTML(x).xpath('//*[@id="{}"]/@value'.format(y)))
        post_data = {
            # '__EVENTVALIDATION': validation,
            '_ctl0:C1:TB_BgSj_Star': '2007-01-01',
            '_ctl0:C1:TB_BgSj_End': datetime.now().strftime('%Y-%m-%d'),
            '_ctl0:C1:BTN_Cx': '查询',
            '_ctl0:C1:HD_Bah': blh,
        }
        doc = self.session.post(url, data=post_data).text
        state = a(doc, '__VIEWSTATE')
        targets = re.findall(r"javascript:__doPostBack\('(.+?)',''\)", doc)
        blbg = [self.chakan_blbg(blh, state, target) for target in targets]
        return blbg

    def chakan_blbg(self, blh, state, target):
        url = self.host + '/zwemr/Examination/PisRptQuery.aspx?bah={}&gh={}'.format(blh, self.user)
        post_data = {
            '__VIEWSTATE': state,
            '__EVENTTARGET': target,
        }
        resp = self.session.post(url, data=post_data)
        doc = etree.HTML(resp.text)
        p = lambda x: ''.join(doc.xpath('//*[@id="_ctl0_C1_{}"]//text()'.format(x)))
        result = {
            # 'binglihao': p('LB_ID'),
            50402: p('LB_Diagresult'),
            50403: p('lblbdzd'),
            50404: p('lblBcbg'),
            50401: p('LB_Reportdt'),
        }
        # print(result)
        return result

    def chaxun_sz_blbg(self, blh):
        # self.session.get(self.host+'/zwemr/Patient/Info.aspx?zyxh={}'.format(idx))
        resp = self.session.get(
            self.host + '/zwemr/Szbzx/BingLiBaoGaoList.aspx?bqid=1041003&bah={}&gh={}'.format(blh, self.user))
        view_state = ''.join(etree.HTML(resp.text).xpath('//*[@id="__VIEWSTATE"]/@value'))
        url = self.host + '/zwemr/Szbzx/BingLiBaoGaoList.aspx?bah={}&gh={}'.format(blh, self.user)
        post_data = {
            '__VIEWSTATE': view_state,
            '__VIEWSTATEENCRYPTED': '',
            '_ctl0:C1:BtnQuery': '查询',
            '_ctl0:C1:txtBgsj1': '2007-01-01',
            '_ctl0:C1:txtBgsj2': datetime.now().strftime('%Y-%m-%d'),
        }
        resp = self.session.post(url, data=post_data)
        if resp.status_code == 200:
            # bgid = etree.HTML(resp.text).xpath('//*[@id="_ctl0_C1_gdvBlbg"]//tr/td/input/@value')
            state = ''.join(etree.HTML(resp.text).xpath('//*[@id="__VIEWSTATE"]/@value'))
            sams = etree.HTML(resp.text).xpath('//input[contains(@id, "Radio")]/@value')
            sz_blbg = [self.chakan_sz_blbg(blh, sam, state) for sam in sams]
            return sz_blbg

    def chakan_sz_blbg(self, blh, sam, state):
        url = self.host + '/zwemr/Szbzx/BingLiBaoGaoList.aspx?bah={}&gh={}'.format(blh, self.user)
        post_data = {
            '__VIEWSTATE': state,
            '__VIEWSTATEENCRYPTED': '',
            'radSm': sam,
            '_ctl0:C1:btnCkbg': '查看报告',
            '_ctl0:C1:hidBgid': sam,
        }
        resp = self.session.post(url, data=post_data)
        blsqid = re.search(r'BingLiBaoGaoPrint\.aspx\?bgid=\d+&blsqid=(\d+)', resp.text)
        if blsqid:
            blsqid = blsqid.group(1)
            response = self.session.get(
                self.host + '/zwemr/Szbzx/BingLiBaoGaoPrint.aspx?bgid={}&blsqid={}'.format(sam, blsqid))
            if response.status_code == 200:
                doc = etree.HTML(response.text)
                a = lambda x: ''.join(doc.xpath('//*[@id="_ctl0_C1_{}"]//text()'.format(x))).strip()
                result = {
                    50301: a('lblBgrq'),
                    50307: a('lblTsrsmyzzhx'),
                    # "dianzixianweijing": a('lblDzxwjc'),
                    50308: a('lblBlzd'),
                    50309: a('lblZj'),
                    # "zhenduanyishi": a('lblZdys'),
                }

                # 肾小球 肾小管
                temp = doc.xpath('//*[@id="_ctl0_C1_lblblms"]/font//text()')
                s = ''
                for i in temp:
                    s += i.replace('\xa0', '').strip()
                k = s.split('：')
                if len(k) > 5:
                    sheng = {
                        50302: k[1][:-3],
                        50303: k[2][:-3],
                        50304: k[3][:-3],
                        50305: k[4][:-3],
                        50306: k[5],
                    }
                    result.update(sheng)

                return result

    def xueyansuo(self, blh):
        # blh = 04870051
        url = 'http://192.168.2.8:8055/Report/SearchReport'
        json_data = {
            "bah": blh,
            "startTime": "2007-01-01",
            "endTime": datetime.now().strftime('%Y-%m-%d'),
            "Types": ["XYS", "PS", "SZB", "LIS-RST"],
        }
        resp = self.session.post(url, json=json_data)
        if len(resp.text) > 10:
            doc = etree.HTML(resp.text)
            result = doc.xpath('//tr')
            xys = []
            m = lambda x, y: ''.join(x.xpath(y)).strip()
            for i in result:
                tupian_url = 'http://192.168.2.8:8055' + m(i, './td[7]/a/@href')
                xys.append({
                    50501: m(i, './td[6]//text()'),
                    50502: m(i, './td[5]//text()'),
                    50503: self.xueyansuo_tupian(tupian_url),
                })
            return xys
        else:
            return []

    def xueyansuo_tupian(self, url):
        from bson import binary
        data = requests.get(url, timeout=15).content
        return binary.Binary(data)

    def main(self, blh):
        ruyuans = []
        changqiyizhus = []
        koufu = []
        zhenji = []
        binganshouye = []
        count = 0
        sz_blbg = []
        idx = set(self.zonghechaxun(blh))
        if idx:
            for i in idx:
                self.session.get(self.host + '/zwemr/Patient/Info.aspx?zyxh={}'.format(i))
                binganshouye.append(self.binganshouye(i, blh))

                if self.ruyuanjilu():
                    ruyuans.append(self.ruyuanjilu())

                changqiyizhus.extend(self.changqiyizhu(i, blh))
                kfyy, zjyy = self.yongyaojilu(i, blh)
                koufu.extend(kfyy)
                zhenji.extend(zjyy)

                if count > 0:
                    continue
                sz_blbg = self.chaxun_sz_blbg(blh) or []
                count += 1

            blbg = self.chaxun_blbg(blh)
            xys = self.xueyansuo(blh)

            result = {
                'binganshouye': binganshouye,
                'gerenbingshi': ruyuans,  # hebingdao gerenbingshi
                'changqiyizhu': changqiyizhus,
                'shenzangbinglibaogao': sz_blbg,
                'binglibaogao': blbg,
                'xysszbbg': xys,
                'cqkfyy': koufu,
                'cqzjyy': zhenji
            }
            return result

    def __call__(self, args, io):
        self.login()
        name = args['Name']
        blh = args['Binglihao']
        if name:
            blh_array = self.zonghechaxun(name)
            if blh: blh_array.append(blh)
            pool = Pool()
            result = pool.map(self.main, [i for i in set(blh_array) if i])
            # result = [self.main(i) for i in set(blh_array) if i]
        elif blh:
            result = [self.main(blh)]
        else:
            result = []
        result = [i for i in result if i]
        io.set_output('Array', result)
        io.push_event('Out')


class YihuiSystem(Action):
    _id = '9ed37096-bc78-47c9-b0d0-654123456122d'
    node_info = {"args": [['Name', 'String', 'e142135d-e9a4-11e9-9dd5-f416630aacec'],
                          ['Binglihao', 'String', 'e14321ad-e9a4-11e9-9dd5-f416630aacec'],
                          ['In', 'Event', 'e7260f40-e9a4-11e9-bc41-f432541254ec']
                          ],
                 "returns": [['Array', 'List', 'e72632531-e9a4-11e9-bb0d-f416630aacec'],
                             ['Out', 'Event', 'e7102f42-e9a4-11e9-ba9b-f4166327acec']]}

    def __init__(self):
        self.host = 'http://192.168.2.155:6060'

    def quchong(self, array):
        seen = set()
        new_array = []
        for a in array:
            temp = tuple(a.items())
            if temp not in seen:
                seen.add(temp)
                new_array.append(a)
        return new_array

    def search_patient(self, blh):
        """
        用病历号搜索病人记录
        血透过来病历号，就是次网页的patientId
        """
        url = self.host + '/EgretWS/EgretService'
        request_data = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><getArchivedPatientBySeries xmlns="http://egret/"><patientId xmlns="">{}</patientId><series xmlns="">0</series><patientName xmlns="" /><cliCode xmlns="">EgretPC</cliCode><updateNo xmlns="">122</updateNo></getArchivedPatientBySeries></soap:Body></soap:Envelope>'.format(
            blh)
        resp = requests.post(url, data=request_data)
        series_code = etree.HTML(resp.text).xpath('//return/series/text()')
        # print(series_code)
        return series_code

    def get_request(self, binglihao, series, request_data):
        url = self.host + '/EgretWS/EgretService'
        request_body = request_data.format(binglihao, series)
        try:
            response = requests.post(url, data=request_body)
            if response.status_code == 200 and response:
                return response.text
        except Exception as e:
            pass

    def parse_tiwendang_data(self, response):
        doc = etree.HTML(response).xpath('//return')
        p = lambda x, y: ''.join(x.xpath(y)).strip()
        for i in doc:
            yield {
                'valtype': p(i, './vitalsignstype/text()'),
                'shuzhi': p(i, './vitalsignsval/text()') + p(i, './unit/text()'),
                'shijian': p(i, './excutetime/text()'),
                'hightval': p(i, './vitalsignshightval/text()'),
            }

    def parse_xuetang_data(self, response):
        doc = etree.HTML(response).xpath('//return')
        p = lambda x, y: ''.join(x.xpath(y)).strip()
        xuetang = [{71002: p(i, './val/text()') + p(i, './unit/text()'),
                    71001: p(i, './createtime/text()')} for i in doc]
        return xuetang

    def patient_info(self, blh):
        url = self.host + '/EgretWS/EgretService'
        para = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><getPatientById xmlns="http://egret/"><patientId xmlns="">{}</patientId><cliCode xmlns="">EgretPC</cliCode><updateNo xmlns="">122</updateNo></getPatientById></soap:Body></soap:Envelope>'.format(
            blh)
        resp = requests.post(url, data=para)
        q = lambda x: ''.join(etree.HTML(resp.text).xpath(x)).strip()
        # ['shengfengzhenghao', 'binglihao', 'juzhenkahao', 'name', 'chushengriqi']
        info = {
            'name': q('//return/patient/name/text()'),
            'shengfengzhenghao': q('//return/sfzhm/text()'),
            'binglihao': blh,
            'juzhenkahao': None,
            'chushengriqi': re.sub(r'T.*', '', q('//return/patient/dob/text()')),
        }
        return info

    def get_data(self, blh):
        tiwendang_para = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><gettemperature xmlns="http://egret/"><type xmlns="">4001</type><type xmlns="">4002</type><type xmlns="">4032</type><type xmlns="">4030</type><type xmlns="">4003</type><type xmlns="">4008</type><type xmlns="">4004</type><type xmlns="">4006</type><type xmlns="">4007</type><type xmlns="">4005</type><type xmlns="">4031</type><type xmlns="">4009</type><type xmlns="">4010</type><type xmlns="">4011</type><type xmlns="">4040</type><type xmlns="">4041</type><type xmlns="">4042</type><type xmlns="">4046</type><type xmlns="">4033</type><type xmlns="">4021</type><type xmlns="">4022</type><type xmlns="">4023</type><type xmlns="">4024</type><type xmlns="">4025</type><type xmlns="">4026</type><type xmlns="">4091</type><type xmlns="">4092</type><type xmlns="">4093</type><type xmlns="">4094</type><type xmlns="">4020</type><patient_id xmlns="">{}</patient_id><series xmlns="">{}</series><cliCode xmlns="">EgretPC</cliCode><updateNo xmlns="">122</updateNo></gettemperature></soap:Body></soap:Envelope>'
        xuetang_para = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><listSimpleReportsByPatientId xmlns="http://egret/"><patientId xmlns="">{}</patientId><series xmlns="">{}</series><startTime xmlns="">2005-12-11T00:00:00</startTime><endTime xmlns="">2060-12-31T23:59:59+08:00</endTime><cliCode xmlns="">EgretPC</cliCode><updateNo xmlns="">122</updateNo></listSimpleReportsByPatientId></soap:Body></soap:Envelope>'
        series_code = self.search_patient(blh)

        tiwen = []  # 4001
        maibo = []  # 4002
        huxi = []  # 4003
        xueya = []  # 4008
        tizhong = []  # 4009
        shengao = []  # 4031
        niaoliang = []  # 4005
        xuetang = []
        # print(set(series_code))
        if series_code:
            for code in set(series_code):  # 一个病人多次住院记录
                tiwendang_resp = self.get_request(blh, code, tiwendang_para)
                for itm in self.parse_tiwendang_data(tiwendang_resp):
                    valtype = itm.pop('valtype')
                    hightval = itm.pop('hightval')  # 舒张压
                    temp_doc = {}
                    if valtype == '4001':
                        temp_doc[70201] = itm['shijian']
                        temp_doc[70202] = itm['shuzhi']
                        tiwen.append(temp_doc)
                    elif valtype == '4002':
                        temp_doc[70101] = itm['shijian']
                        temp_doc[70102] = itm['shuzhi']
                        maibo.append(temp_doc)
                    elif valtype == '4003':
                        temp_doc[70301] = itm['shijian']
                        temp_doc[70302] = itm['shuzhi']
                        huxi.append(temp_doc)
                    elif valtype == '4008':  # 脉搏
                        temp_doc[70401] = itm['shijian']
                        temp_doc[70402] = ''.join([hightval, '/', itm['shuzhi']])
                        xueya.append(temp_doc)
                    elif valtype == '4009':
                        temp_doc[70601] = itm['shijian']
                        temp_doc[70602] = itm['shuzhi']
                        tizhong.append(temp_doc)
                    elif valtype == '4031':
                        temp_doc[70501] = itm['shijian']
                        temp_doc[70502] = itm['shuzhi']
                        shengao.append(temp_doc)
                    elif valtype == '4005':
                        temp_doc[70701] = itm['shijian']
                        temp_doc[70702] = itm['shuzhi']
                        niaoliang.append(temp_doc)

                xuetang_resp = self.get_request(blh, code, xuetang_para)
                xuetang.extend(self.parse_xuetang_data(xuetang_resp))

            info = self.patient_info(blh)
            result = {
                'binglihao': blh,
                't': self.quchong(tiwen),
                'p': self.quchong(maibo),
                'r': self.quchong(huxi),
                'bp': self.quchong(xueya),
                'tizhong': self.quchong(tizhong),
                'shengao': self.quchong(shengao),
                'niaoliang': self.quchong(niaoliang),
                'xuetang': self.quchong(xuetang),
                'ruliang': None,
                'chuliang': None,
            }
            result.update(info)
            return result

    def search_patient_with_name(self, name):
        url = self.host + '/EgretWS/EgretService'
        name = name.encode('utf-8').decode('latin1')
        para = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><getArchivedPatientBySeries xmlns="http://egret/"><patientId xmlns="" /><series xmlns="">0</series><patientName xmlns="">{}</patientName><cliCode xmlns="">EgretPC</cliCode><updateNo xmlns="">122</updateNo></getArchivedPatientBySeries></soap:Body></soap:Envelope>'.format(
            name)
        resp = requests.post(url, data=para)
        blh_arry = etree.HTML(resp.text).xpath('//return/id/text()')
        return blh_arry

    def __call__(self, args, io):
        name = args['Name']
        blh = args['Binglihao']

        if name:
            blh_array = self.search_patient_with_name(name)
            if blh: blh_array.append(blh)
            # pool = Pool()
            # result = pool.map(self.get_data, [i for i in set(blh_array) if i])
            result = [self.get_data(i) for i in set(blh_array) if i]
        else:
            result = [self.get_data(blh)]
        result = [i for i in result if i]
        io.set_output('Array', result)
        io.push_event('Out')


class YingXiang(Action):
    _id = '9ed37096-bc78-47c9-2021-654fef1f8122d'
    node_info = {"args": [['Name', 'String', 'e1460f3d-e9a4-11e9-9dd5-32ad630aacec'],
                          ['Binglihao', 'String', 'e3250f3d-e9a4-652a-9dd5-f416630aacec'],
                          ['In', 'Event', 'e7260f40-e9a4-3215-bc41-f416631254ec']
                          ],
                 "returns": [['Array', 'List', 'e726345a1-e9a4-11e9-bb0d-f416630aacec'],
                             ['Out', 'Event', 'e710362a-e9a4-11e9-ba9b-f416630aacec']]}

    def __init__(self):
        self.host = 'http://192.168.33.115'

    def get_index(self, **post_data):
        url = self.host + '/Home/GetWorkListView'
        if post_data.get('PatientsID'):  # 提取访问详情页需要的参数
            resp = requests.post(url, data=post_data)
            paras = etree.HTML(resp.text).xpath('//table/tbody/tr/td[1]/text()')
            return paras
        elif post_data.get('PatientsAlias'):
            resp = requests.post(url, data=post_data)
            blh_arry = etree.HTML(resp.text).xpath('//table/tbody/tr/td[5]/text()')
            return blh_arry

    def get_other_index_data(self, resp, page, **post_data):
        p = lambda x, y: ''.join(etree.HTML(x).xpath(y)).strip()
        total = p(resp.text, '//*[@id="hidResultTotal"]/@value')
        item_num = p(resp.text, '//*[@id="hidPageNum"]/@value')
        pages = int(total) // int(item_num) + 1
        ret = []
        while page < pages:
            page += 1
            post_data.update({"CurrentPageIndex": page})
            ret.extend(self.get_index(**post_data))
        return ret

    def get_data(self, key, page=1):
        url = self.host + '/Home/GetWorkListView'
        post_data = {
            'AdmissionSource': '50,10,100,1',
            'OrderBy': 'False',
            'StartTime': '2000-01-01',
            'EndTime': datetime.now().strftime('%Y-%m-%d'),
            'CurrentPageIndex': page,
        }
        if key.isdigit():  # key为病历号, 病历号检索
            post_data.update({'PatientsID': key})
            resp = requests.post(url, data=post_data)
            # 提取请求每条记录所需的参数
            paras = etree.HTML(resp.text).xpath('//table/tbody/tr/td[1]/text()')
            others = self.get_other_index_data(resp, page, **post_data)
            paras.extend(others)
            return paras
        else:  # key 为姓名, 用姓名搜索病历号
            name = key.encode('unicode-escape').decode().replace('\\', '%')
            post_data.update({'PatientsAlias': name})
            resp = requests.post(url, post_data)
            blh_s = etree.HTML(resp.text).xpath('//table/tbody/tr/td[5]/text()')
            others = self.get_other_index_data(resp, page, **post_data)
            blh_s.extend(others)
            # print(blh_s)
            return blh_s

    def get_detail(self, para):
        url = self.host + '/Report/Report'
        values = para.split('|')
        keys = ('StudiesIndex', 'ResultsIndex', 'AccessionNumber', 'AdmissionID', 'PatientsID')
        param = dict(zip(keys, values))
        param.update({'DBclick': 'true'})
        resp = requests.get(url, data=param)
        p = lambda x: ''.join(etree.HTML(resp.text).xpath(x)).strip().replace('&nbsp', '')
        # [50106, 50101, 0, 50103, 50105]
        result = {
            50101: param.get('PatientsID'),
            50103: p('//*[@id="fldPatientInfo"]/table/tr[2]/td/label/text()'),
            50105: p('//*[@id="fldPatientInfo"]/table/tr[7]/td/label/text()'),
            50106: p('//*[@id="fldPatientInfo"]/table/tr[8]/td/label/text()'),

            50205: p('//*[@id="tdContentMiddle"]/div/table/tr[3]/td/fieldset/text()'),
            50203: p('//*[@id="fldPatientInfo"]/table/tr[14]/td/label/text()'),
            50202: p('//*[@id="fldPatientInfo"]/table/tr[10]/td/label/text()'),
            50204: p('//*[@id="tdContentMiddle"]/div/table/tr[2]/td/fieldset/text()'),
            50201: p('//*[@id="fldPatientInfo"]/table/tr[18]/td/label/text()'),
        }
        # print(result)
        return result

    def main(self, blh, name=None):
        if name:
            blh_array = self.get_data(name)
            if blh: blh_array.append(blh)
            # pool = Pool()
            result = []
            for i in set(blh_array):
                result.extend([self.get_detail(para) for para in set(self.get_data(i))])
        elif blh:
            result = [self.get_detail(para) for para in set(self.get_data(blh))]
        else:
            result = []
        return result

    def __call__(self, args, io):
        # blh = '00764982'
        # name = '孙玉祥'
        name = args['Name']
        blh = args['Binglihao']

        result = self.main(blh, name)

        io.set_output('Array', result)
        io.push_event('Out')
