# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by LiQing.
contact blacknepia@dingtail.com for more information
contact blacknepia@dingtail.com for more information
"""
from runtime.Action import Action
import requests
from lxml import html, etree 
import json
import pymongo
import decimal
from copy import deepcopy
from datetime import datetime 


class Huayan(Action):
    #血透系统  化验独有节点
    _id = '76fc0440-e968-11e9-952a-8cec4bd887f3'
    node_info = {"args": [['title_dict', 'Dict', 'e7260f3d-e9a4-11e9-9dd5-f416630aacec'],
                          ['key_dict', 'Dict', 'e7260f3e-e9a4-11e9-b322-f416630aacec'],
                          ['In', 'Event', 'e7260f40-e9a4-11e9-bc41-f416630aacec']],
                 "returns": [['huayan_data', 'List', 'e7260f41-e9a4-11e9-bb0d-f416630aacec'],
                             ['Out', 'Event', 'e7260f42-e9a4-11e9-ba9b-f416630aacec']]}
    def __call__(self, args, io):
        huayanshuju_list=[]
        title_dict = args['title_dict']
        key_dict  = args['key_dict']
        dict_title  = {}
        if title_dict:
            for i in title_dict[1:]:
                list_a = []
                for key,value in i.items():
                    list_a.append(value)
              
                if list_a[1].isdigit():
                    dict_title[list_a[1]]=list_a[0]
                else:


                    dict_title[list_a[0]]=list_a[1]
        data_list = key_dict['data']

        dict_key  = {}

        for i in data_list:
            for key,value in i.items():
                if key != 'panelsId':
                   dict_key[key]=value.replace('&nbsp;','')
            huayanshuju = {}

            for key,value in dict_key.items():
               
                
                huayanshuju[dict_title[key]] = value              

            huayanshuju_list.append(huayanshuju)  
        
        io.set_output('huayan_data',huayanshuju_list)
        io.push_event('Out')                     


class ProgressNotexpath(Action):
    """检查报告独有节点"""
    _id = '00b7db9c-f468-11e9-8c34-8cec4bd887f3'
    node_info = {"args": [['con_str', 'String', '0da80ee2-10ed-11ea-ada6-8cec4bd887f3'],
                          ['In', 'Event', '0e19df2e-10ed-11ea-9e3d-8cec4bd887f3']],
                 "returns": [['doc_dict', 'Dict', '0e7573dc-10ed-11ea-ab57-8cec4bd887f3'],
                             ['Out', 'Event', '1982f3b4-10ed-11ea-be68-8cec4bd887f3']]}

    def __call__(self, args, io):
        con = args['con_str']
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 6.1; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)',
            'x-ajaxpro-method': 'JyJg',
            'Content-Type': 'application/json',
        }
        url = 'http://192.168.17.102/zwemr/ajaxpro/Examination_LisRptQuery,App_Web_etv11kkj.ashx'
        # print(con)
        doc_dict = {}
        data_dict = {}
        etree = html.etree
        tree = etree.HTML(con)
        # 送检情况div
        div = tree.xpath('//*[@id="_ctl0_C1_P_SjQk"]/table[position()>1]')
        div_dict = {}
        div_list = []
        for i in div:
            # 组序号
            number = i.xpath('./tr/td[3]//text()')
            number = ''.join(number)
            number = ''.join(number.split())

            # 组名称
            name = i.xpath('./tr/td[4]//text()')
            name = ''.join(name)
            name = ''.join(name.split())
            # 送检时间
            start_name = i.xpath('./tr/td[5]//text()')
            start_name = ''.join(start_name)
            start_name = ''.join(start_name.split())
            # 报告时间
            end_name = i.xpath('./tr/td[6]//text()')
            end_name = ''.join(end_name)
            end_name = ''.join(end_name.split())
            data_dict['zxh'] = number
            data_dict["bah"] = "03978273"
            data_dict["t"] = ''
            r = requests.post(url=url, data=json.dumps(data_dict), headers=headers)
            content = r.text
            etree = html.etree
            tree = etree.HTML(content)
            # 项目名称 ，结果 ，单位 ，参考范围 table 数量
            tables = tree.xpath('//table[position()>0]')

            table_dict = {}
            table_dict2 = {}
            list_table = []
            for table in tables:
                # 项目名称
                table_name = table.xpath('./tr/td[2]/a/text()')
                table_dict['项目名称'] = table_name
                # 结果
                table_result = table.xpath('./tr/td[3]//text()')
                table_dict['结果'] = table_result
                # 箭头
                table_jt = table.xpath('./tr/td[4]//text()')
                table_dict['趋势'] = table_jt
                # 单位
                table_dw = table.xpath('./tr/td[5]//text()')
                table_dict['单位'] = table_dw
                # 参考范围
                table_fw = table.xpath('./tr/td[6]//text()')
                table_dict['参考范围'] = table_fw
                for key, value in table_dict.items():
                    value = ''.join(value)
                    value = ''.join(value.split())
                    table_dict2[key] = value
                list_table.append(table_dict2)
                table_dict = {}
                table_dict2 = {}

            div_dict[name] = list_table
            div_list.append(div_dict)
            div_dict = {}
        doc_dict['检查报告'] = div_list

        io.set_output('doc_dict', doc_dict)
        io.push_event('Out')


class Clinical_imaging(Action):
    '''临床影像系统独有节点'''
    _id = '21eb75d8-10f0-11ea-8bb9-8cec4bd887f3'
    node_info = {"args": [['doc_list', 'List', '228ff588-10f0-11ea-8fa1-8cec4bd887f3'],
                          ['In', 'Event', '2d06415c-10f0-11ea-8dfd-8cec4bd887f3']],
                 "returns": [['doc_dict', 'Dict', '2e604d54-10f0-11ea-9422-8cec4bd887f3'],
                             ['Out', 'Event', '371a81d2-10f0-11ea-b99e-8cec4bd887f3 ']]}

    def __call__(self, args, io):
        number_list = args['doc_list']
        dict1 = {}
        dict2 = {}
        dict3 = {}
        list1 = []
        dict4 = {}
        list2 = []
        doc_dict = {}
        url = "http://192.168.33.115/Report/Report/"
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 6.1; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)'}
        #print(number_list)
        for i in number_list:
            i = ''.join(i)
            i = i.split('|')
            #print(i)
            dict1['StudiesIndex'] = i[0]
            dict1['ResultsIndex'] = i[1]
            dict1['AccessionNumber'] = i[2]
            dict1['PatientsID'] = i[4]
            dict1['AdmissionID'] = i[3]
            dict1['DBclick'] = 'true'
     
            response = requests.get(url=url, headers=headers, params=dict1)
            con = response.text
            
            etree = html.etree
            tree = etree.HTML(con)
            dict2['病历号'] = tree.xpath('//*[@class="tabPatient"]/tr[1]//td//text()')
            dict2['病人编号'] = tree.xpath('//*[@class="tabPatient"]/tr[1]//td//text()')
            dict2['病人姓名'] = tree.xpath('//*[@class="tabPatient"]/tr[2]//td//text()')
            
 
            dict2['病人性别'] = tree.xpath('//*[@class="tabPatient"]/tr[3]//td//text()')
           
            dict2['出生日期'] = tree.xpath('//*[@class="tabPatient"]/tr[7]//td//text()')
            dict2['证件号码'] = tree.xpath('//*[@class="tabPatient"]/tr[8]//td//text()')
            jianchahao = tree.xpath('//*[@id="fldPatientInfo"]/table//tr[9]/td/label/text()')
            if jianchahao :
             jianchahao = "检查号" + jianchahao[0]
            else: jianchahao ='dasd'
            dict2['检查类型'] = tree.xpath('//*[@class="tabPatient"]/tr[10]//td//text()')
            dict2['检查项目'] = tree.xpath('//*[@id="fldPatientInfo"]/table//tr[14]/td//text()')

            dict2['检查日期'] = tree.xpath('//*[@class="tabPatient"]/tr[18]//td//text()')


            dict2['影像表现']=tree.xpath('//*[@class="DvContentTable"]/tr[2]//td/fieldset/text()')
            dict2['诊断结论']=tree.xpath('//*[@class="DvContentTable"]/tr[3]//td/fieldset/text()')
            for key, value in dict2.items():
                value = ''.join(value)
                value = ''.join(value.split())
                value = value.strip('&nbsp')
                dict3[key] = value

            list1.append(dict3)
            dict4[jianchahao] = list1
            list2.append(dict4)
            dict1 = {}
            dict2 = {}
            dict3 = {}
            list1 = []
            dict4 = {}
        doc_dict["检查报告"] = list2

        io.set_output('doc_dict', doc_dict)
        io.push_event('Out')


class A_hemogram(Action):
    '''血液透析记录表'''
    _id = '99ae4fcc-10f0-11ea-9ee0-8cec4bd887f3'
    node_info = {"args": [['doc_list', 'List', '9abaeb98-10f0-11ea-8f11-8cec4bd887f3'],
                          ['In', 'Event', '9b4403c2-10f0-11ea-be0b-8cec4bd887f3']],
                 "returns": [['doc_dict', 'Dict', 'acbba270-10f0-11ea-9c87-8cec4bd887f3'],
                             ['Out', 'Event', 'ad6dd276-10f0-11ea-8fa5-8cec4bd887f3 ']]}

    def __call__(self, args, io):
        number_list = args['doc_list']
        url = "http://192.168.1.31/webService/"
        headers = {
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 6.1; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; InfoPath.2)'
        }
        dict1 = {}
        dict2 = {}
        dict3 = {}
        list1 = []
        list2 = []
        doc_dict = {}

        for i in number_list:
            url_s = url + i
            respon = requests.get(url=url_s, headers=headers)
            con = respon.text
            etree = html.etree
            tree = etree.HTML(con)
            date = tree.xpath('/html/body/div/table[2]//tr[1]/td[6]//text()')
            date = ''.join(date)
            dict1['血透病历号'] = tree.xpath('/html/body/div/table[2]//tr[1]/td[2]//text()')
            dict1['姓名'] = tree.xpath('/html/body/div/table[2]//tr[1]/td[3]//text()')
            dict1['血透床位号'] = tree.xpath('/html/body/div/table[2]//tr[1]/td[4]//text()')
            dict1['住院号'] = tree.xpath('/html/body/div/table[2]//tr[1]/td[5]//text()')
            dict1['性别'] = tree.xpath('/html/body/div/table[3]//tr[1]/td[2]/text()')
            dict1['病区床号'] = tree.xpath('/html/body/div/table[3]//tr[1]/td[3]/text()')
            dict1['透析号'] = tree.xpath('/html/body/div/table[3]//tr[1]/td[4]/text()')
            dict1['透析方式'] = tree.xpath('/html/body/div/table[3]//tr[2]/td[1]/text()')
            dict1['透析机型'] = tree.xpath('/html/body/div/table[3]//tr[2]/td[2]/text()')
            dict1['透析器型号'] = tree.xpath('/html/body/div/table[3]//tr[2]/td[3]/text()')
            dict1['透析器膜面积'] = tree.xpath('/html/body/div/table[3]//tr[2]/td[4]/text()')
            dict1['透析液处方K+'] = tree.xpath('/html/body/div/table[3]//tr[3]/td[1]/text()')
            dict1['Na+'] = tree.xpath('/html/body/div/table[3]//tr[3]/td[2]/text()')
            dict1['Ca+'] = tree.xpath('/html/body/div/table[3]//tr[3]/td[3]/text()')
            dict1['透析液流量'] = tree.xpath('/html/body/div/table[3]//tr[3]/td[4]/text()')
            dict1['血管通路'] = tree.xpath('/html/body/div/table[3]//tr[4]/td[1]/text()')
            dict1['血管通路部位'] = tree.xpath('/html/body/div/table[3]//tr[4]/td[2]/text()')
            dict1['导管型号'] = tree.xpath('/html/body/div/table[3]//tr[4]/td[3]/text()')
            dict1['封管液'] = tree.xpath('/html/body/div/table[3]//tr[4]/td[4]/text()')
            dict1['诊断'] = tree.xpath('/html/body/div/table[4]//tr[2]/td[1]/text()')
            dict1['前次透析时间'] = tree.xpath('/html/body/div/table[5]//tr[2]/td[2]/text()')
            dict1['透析间期尿量'] = tree.xpath('/html/body/div/table[5]//tr[2]/td[4]/text()')
            dict1['前次透析后反应'] = tree.xpath('/html/body/div/table[5]//tr[2]/td[6]/text()')
            dict1['透析前体温'] = tree.xpath('/html/body/div/table[5]//tr[3]/td[2]/text()')
            dict1['透析前心率'] = tree.xpath('/html/body/div/table[5]//tr[3]/td[4]/text()')
            dict1['透析前收缩压'] = tree.xpath('/html/body/div/table[5]//tr[3]/td[6]/text()')
            dict1['透析前舒张压'] = tree.xpath('/html/body/div/table[5]//tr[3]/td[8]/text()')
            dict1['测血压部位'] = tree.xpath('/html/body/div/table[5]//tr[4]/td[2]/text()')
            dict1['其他'] = tree.xpath('/html/body/div/table[5]//tr[4]/td[4]/text()')
            dict1['设定透析时间'] = tree.xpath('/html/body/div/table[6]//tr[2]/td[2]/text()')
            dict1['干体重'] = tree.xpath('/html/body/div/table[6]//tr[3]/td[2]/text()')
            dict1['前次透析后体重'] = tree.xpath('/html/body/div/table[6]//tr[3]/td[4]/text()')
            dict1['透析前体重'] = tree.xpath('/html/body/div/table[6]//tr[3]/td[6]/text()')
            dict1['减衣服'] = tree.xpath('/html/body/div/table[6]//tr[3]/td[8]/text()')
            dict1['净体重'] = tree.xpath('/html/body/div/table[6]//tr[5]/td[2]/text()')
            dict1['透析间期体重增加'] = tree.xpath('/html/body/div/table[6]//tr[5]/td[4]/text()')
            dict1['透析间期体重增加率'] = tree.xpath('/html/body/div/table[6]//tr[5]/td[6]/text()')
            dict1['拟脱水'] = tree.xpath('/html/body/div/table[6]//tr[5]/td[8]/text()')
            dict1['抗凝剂'] = tree.xpath('/html/body/div/table[6]//tr[7]/td[2]/text()')
            dict1['首剂'] = tree.xpath('/html/body/div/table[6]//tr[7]/td[4]/text()')
            dict1['维持量'] = tree.xpath('/html/body/div/table[6]//tr[7]/td[6]/text()')
            dict1['实际透析时间'] = tree.xpath('/html/body/div/table[9]//tr[2]/td[2]/text()')
            dict1['透析时间完成率'] = tree.xpath('/html/body/div/table[9]//tr[2]/td[4]/text()')
            dict1['透析后净体重'] = tree.xpath('/html/body/div/table[9]//tr[2]/td[6]/text()')
            dict1['体重下降'] = tree.xpath('/html/body/div/table[9]//tr[2]/td[8]/text()')
            dict1['透析后体温'] = tree.xpath('/html/body/div/table[9]//tr[3]/td[2]/text()')
            dict1['透析后收缩压'] = tree.xpath('/html/body/div/table[9]//tr[3]/td[4]/text()')
            dict1['透析后舒张压'] = tree.xpath('/html/body/div/table[9]//tr[3]/td[6]/text()')
            dict1['透析后心率'] = tree.xpath('/html/body/div/table[9]//tr[3]/td[8]/text()')
            dict1['插管使用方向'] = tree.xpath('/html/body/div/table[9]//tr[4]/td[2]/text()')
            dict1['插管出口情况'] = tree.xpath('/html/body/div/table[9]//tr[4]/td[4]/text()')
            dict1['处理'] = tree.xpath('/html/body/div/table[9]//tr[4]/td[6]/text()')
            dict1['血管通路血流情况'] = tree.xpath('/html/body/div/table[9]//tr[5]/td[2]/text()')
            dict1['血流量'] = tree.xpath('/html/body/div/table[9]//tr[5]/td[4]/text()')
            dict1['透析器凝血级'] = tree.xpath('/html/body/div/table[9]//tr[5]/td[6]/text()')
            dict1['血路管凝血级'] = tree.xpath('/html/body/div/table[9]//tr[5]/td[8]/text()')
            dict1['抗凝剂总量'] = tree.xpath('/html/body/div/table[9]//tr[6]/td[2]/text()')
            dict1['鱼精蛋白'] = tree.xpath('/html/body/div/table[9]//tr[6]/td[4]/text()')
            for key, value in dict1.items():
                value = ''.join(value)
                value = ''.join(value.split())
                value = value.strip('&nbsp').strip('\xa0透析号：').strip('血透病历号：').strip('姓名：').strip('血透床位号：').strip(
                    '住院号：')
                dict3[key] = value
            list1.append(dict3)
            dict2[date] = list1
            list2.append(dict2)
            dict1 = {}
            dict2 = {}
            dict3 = {}
            list1 = []
        doc_dict["血液透析记录表"] = list2
        io.set_output('doc_dict', doc_dict)
        io.push_event('Out')


class YihuiRequest(Action):
    _id = '507c4cde-10f4-23ea-b977-8cec4bd667f3'
    node_info = {"args": [['url', 'String', '50df5792-10f4-11ea-a522-8cec4bd337f3'],
                          ['patient_id', 'String', '513bdcb8-10f4-52ea-b2af-8cec4bd347f3'],
                          ['series', 'String', '5dec9388-10f4-52ea-93f0-8cec4bd637f3'],
                          ['request_data', 'String', '5dec9834-13f4-52ea-93f0-8cec4bd637f3'],
                          ['In', 'Event', '6e02c34c-12f4-11ea-93d0-8cec4bd917f3']],
                 "returns": [['response', 'String', '6e6e3434-10f4-38ea-9724-8cec4bd887f3'],
                             ['exceptions', 'String', '5d718a46-10f4-24ea-a06d-8cec4bd727f3'],
                             ['Except', 'Event', '5dbf74fa-10f4-28ea-8e6d-8cec4bd517f3'],
                             ['Out', 'Event', '6ec41528-50f4-11ea-90cf-8cec4bd557f3']]}
   
    def __call__(self, args, io):
        url = args['url']
        patient_id = args['patient_id']
        series = args['series']
        request_data = args['request_data']

        if patient_id and series:
            request_body = request_data.format(patient_id, series)
        elif patient_id and not series:
            request_body = request_data.format(patient_id.encode('utf-8').decode('latin1'))
            # print(request_body)
        elif not patient_id and not series:
            request_body = request_data

        response = requests.post(url, data=request_body)
        if response.status_code == 200:
            io.set_output('response', response.text)
            io.push_event('Out')
        else:
            io.set_output('exceptions', response.status_code)
            io.push_event('Except')
       
        
class YihuiPersonalTiZheng(Action):
    _id = '507c4cde-10f4-23ea-b977-87ujambv67f3'
    node_info = {"args": [['doc_list', 'List', '50df5792-10f4-11ea-a522-8cec7hac67f3'],
                          ['binglihao', 'String', '518543v8-10f4-52ea-b2af-8cec4bd347f3'],
                          ['In', 'Event', '6e02c34c-12f4-11ea-93d0-8cvjkkb917f3']],
                 "returns": [['tizheng', 'Dict', '6e6e3434-10f4-38ea-9724-8cecabca87f3'],
                             ['Out', 'Event', '6ec41528-50f4-11ea-90cf-8cec5421f7f3']]}
   # {'binglihao': './patientid/text()', 'series': './series/text()', 'xingming': './patientname/text()'}
    def __call__(self, args, io):
        return_list = args['doc_list']
        binglihao = args['binglihao']
        shengmingtizheng = {}

        tiwendang_para = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><gettemperature xmlns="http://egret/"><type xmlns="">4001</type><type xmlns="">4002</type><type xmlns="">4032</type><type xmlns="">4030</type><type xmlns="">4003</type><type xmlns="">4008</type><type xmlns="">4004</type><type xmlns="">4006</type><type xmlns="">4007</type><type xmlns="">4005</type><type xmlns="">4031</type><type xmlns="">4009</type><type xmlns="">4010</type><type xmlns="">4011</type><type xmlns="">4040</type><type xmlns="">4041</type><type xmlns="">4042</type><type xmlns="">4046</type><type xmlns="">4033</type><type xmlns="">4021</type><type xmlns="">4022</type><type xmlns="">4023</type><type xmlns="">4024</type><type xmlns="">4025</type><type xmlns="">4026</type><type xmlns="">4091</type><type xmlns="">4092</type><type xmlns="">4093</type><type xmlns="">4094</type><type xmlns="">4020</type><patient_id xmlns="">{}</patient_id><series xmlns="">{}</series><cliCode xmlns="">EgretPC</cliCode><updateNo xmlns="">122</updateNo></gettemperature></soap:Body></soap:Envelope>'
        xuetang_para = '<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"><soap:Body><listSimpleReportsByPatientId xmlns="http://egret/"><patientId xmlns="">{}</patientId><series xmlns="">{}</series><startTime xmlns="">2019-12-11T00:00:00</startTime><endTime xmlns="">2019-12-31T23:59:59+08:00</endTime><cliCode xmlns="">EgretPC</cliCode><updateNo xmlns="">122</updateNo></listSimpleReportsByPatientId></soap:Body></soap:Envelope>'

        tiwen = []  # 4001
        maibo = []  # 4002
        huxi = []   # 4003
        xueya = []  # 4008
        tizhong = []  # 4009
        shengao = []  # 4031
        niaoliang = []  # 4005
        xuetang = []

        for item in return_list:  # 一个病人多次住院记录
            # binglihao = item.xpath('./patientid/text()')
            series = item.xpath('./series/text()')

            tiwendang_resp = self.get_data(binglihao, series, tiwendang_parse)
            if tiwendang_resp:
                for itm in self.parse_tiwendang_data(tiwendang_resp):
                    valtype = itm.pop('valtype')
                    if valtype == '4001':
                        tiwen.append(itm)
                    elif valtype == '4002':
                        maibo.append(itm)
                    elif valtype == '4003':
                        huxi.append(itm)
                    elif valtype == '4008':
                        xueya.append(itm)
                    elif valtype == '4009':
                        tizhong.append(itm)
                    elif valtype == '4031':
                        shengao.append(itm)
                    elif valtype == '4005':
                        niaoliang.append(itm)

            xuetang_resp = self.get_data(binglihao, series, xuetang_parse)
            if xuetang_resp:
                xuetang = self.parse_xuetang_data(xuetang_resp)

        shengmingtizheng['binglihao'] = binglihao
        shengmingtizheng['t'] = tiwen 
        shengmingtizheng['p'] = maibo
        shengmingtizheng['r'] = huxi 
        shengmingtizheng['bp'] = xueya 
        shengmingtizheng['tizhong'] = tizhong 
        shengmingtizheng['shengao'] = shengao
        shengmingtizheng['niaoliang'] = niaoliang
        shengmingtizheng['xuetang'] = xuetang
        shengmingtizheng['ruliang'] = []
        shengmingtizheng['chuliang'] = []
        out_data = {'shengmingtizheng': shengmingtizheng}
        io.set_output('tizheng', out_data)
        io.push_event('Out')


    def get_data(self, binglihao, series, request_data):
        url = 'http://192.168.2.155:6060/EgretWS/EgretService'
        request_body = request_data.format(binglihao, series)
        try:
            response = requests.post(url, data=request_body)
            if response.status_code == 200 and response:
                return response.text
            else:
                print(response.status_code)
        except Exception as e:
            print('get_data', e)

    def parse_tiwendang_data(self, response):
        tree = etree.HTML(response)
        result_data = tree.xpath('//return')
        if result_data:
            for item in result_data:
                vitalsignstype = item.xpath('./vitalsignstype/text()')[0]
                unit = ''.join(item.xpath('./unit/text()'))
                vitalsignsval = item.xpath('./vitalsignsval/text()')[0]
                executetime = item.xpath('./excutetime/text()')[0]
                yield  {'valtype': vitalsignstype, 'shuzhi': vitalsignsval+unit, 'shijian': executetime}


    def parse_xuetang_data(self, response):
        tree = etree.HTML(response)
        result_data = tree.xpath('//return')

        xuetang = []
        if result_data:
            for item in result_data:
                val = item.xpath('./val/text()')[0]
                unit = item.xpath('./unit/text()')[0] 
                createtime = item.xpath('./createtime/text()')[0]

                xuetang.append(
                    {'shuzhi': val+unit, 'shijian': createtime}
                    )  
        return xuetang     


class MenZhenData(Action):
    _id = '507c4cde-10f4-23ea-b977-1023952ajvzf3'
    node_info = {"args": [['doc_list', 'Tuple', '50df5792-3244-542a-a522-8cec7hac67f3'],
                          ['jbxx_sql', 'String', '50df5792-3244-542a-a522-8cec7h63251a'],
                          ['koufuyao_sql', 'String', '518543v8-10f4-6545-b2af-8ce8523147f3'],
                          ['koufuyao_keys', 'List', '9654hack-10f4-6523-b2af-8cec4bd347f3'],
                          ['koufuyao_format', 'Dict', 'jajklxg34-10f4-52ea-b2af-8cec4bd347f3'],
                          ['zhenjiyao_sql', 'String', '518543v8-10f4-52ea-b2af-8jzblakp47f3'],
                          ['zhenjiyao_keys', 'List', '518543v8-10f4-aclz-b2af-653254d347f3'],
                          ['zhenjiyao_format', 'Dict', 'jfalvr3v8-10f4-52ea-b2af-ackl45d347f3'],
                          ['In', 'Event', '6e02c34c-12f4-11ea-93d0-7632avl917f3']],
                 "returns": [
                             ['Out', 'Event', '6ec41528-50f4-11ea-90cf-863214abf7f3']]}

    def __init__(self):
        mongo_url = '192.168.66.108'
        self.mongo_db = 'xuetou'
        mongo_chart = 'menzhen'
        client = pymongo.MongoClient(mongo_url)
        db = client[self.mongo_db]
        self.collection = db[mongo_chart]

    def __call__(self, args, io):

        doc_list = args['doc_list']
        jbxx_sql = args['jbxx_sql'] 
        #'select sfzh, bah, jzkh, xm, csrq from gy_brjbxxk where {}'

        koufuyao_sql = args['koufuyao_sql']
        koufuyao_keys = args['koufuyao_keys']
        koufuyao_format = args['koufuyao_format']

        zhenjiyao_sql = args['zhenjiyao_sql']
        zhenjiyao_keys = args['zhenjiyao_keys']
        zhenjiyao_format = args['zhenjiyao_format']

        

        sfzh, blh, jzkh, xm, csrq, patient_id = doc_list
        print(doc_list)

        
        sfzh_out, blh_out, jzkh_out, xm_csrq_out = [[] for i in range(4)]
        if sfzh: 
            sfzh_out = self.get_oracal_data(jbxx_sql.format("sfzh='%s'" % sfzh))
        if blh:
            blh_out = self.get_oracal_data(jbxx_sql.format("bah='%s'" % blh))
        if jzkh:
            jzkh_out = self.get_oracal_data(jbxx_sql.format("jzkh='%s'" % jzkh))
        if xm and csrq:
            xm_csrq_out = self.get_oracal_data(jbxx_sql.format("xm='%s'" % xm))
        
        all_data = {
            'sfzh_out': sfzh_out,
            'blh_out': blh_out,
            'jzkh_out': jzkh_out,
            'xm_csrq_out': xm_csrq_out
        }

        first_level = all_data['sfzh_out']
        for item in all_data['blh_out']:
            if item['SFZH'] != sfzh or not item['SFZH']:
                first_level.append(item)
        for ite in all_data['jzkh_out']:
            if (ite['SFZH'] != sfzh and ite['BAH'] != blh) or not(ite['SFZH'] or ite['BAH']):
                first_level.append(ite)
        for it in all_data['xm_csrq_out']:
            if self.mongo_db == 'futou':
                if it['CSRQ'] and csrq.strftime('%Y-%m-%d') == it['CSRQ'].split(' ')[0]:
                    if not (it['SFZH'] or it['BAH'] or it['JZKH']):
                        first_level.append(it)
            elif self.mongo_db == 'xuetou':            
                if it['CSRQ'] and csrq.split(' ')[0] == it['CSRQ'].split(' ')[0]:
                    if not (it['SFZH'] or it['BAH'] or it['JZKH']):
                        first_level.append(it)

        jzkh_list = [i['JZKH'] for i in first_level]
        # jzkh_list = ['A13781996', 'B22639956']
        
        changqikoufuyongyao, changqizhenjiyongyao = [], []
        if jzkh_list:
            if len(jzkh_list) == 1:
                dat = "('%s')" % jzkh_list[0]
            else:
                dat = tuple(jzkh_list)
            
            changqikoufuyongyao = self.get_format_data(koufuyao_sql.format(dat))
            
            changqizhenjiyongyao = self.get_format_data(zhenjiyao_sql.format(dat))

        one_data = {
                'patient_id': int(patient_id),
                'yongyaojilu': {
                'changqikoufuyongyao': changqikoufuyongyao,
                'changqizhenjiyongyao': changqizhenjiyongyao}
                }

        # self.collection.insert_one(one_data)

        self.collection.update_one({'patient_id': one_data['patient_id']}, {'$set': one_data}, upsert=True)
        print(one_data, '\n')

    def get_format_data(self, sql):
        raw_data = self.get_oracal_data(sql)

        temp = []
        for row in raw_data:
            try:
                row_format = {'kaiyaoshijian': row['CFRQ'],
                              'yaowumingcheng': row['YPMC'],
                              'guige': row['YPGG'],
                              'yicijiliang': row['YCJL'],
                              'danwei': row['JLDW'],
                              'yongfa': row['FYFS'],
                              'yongyaopinlv': row['PL'], 
                              'tingzhishijian': row['TZSJ'], 
                              'shujulaiyuan': 2}
                temp.append(row_format)
            except Exception as e:
                print(e)
        return temp 
        


    def get_oracal_data(self, sql):
        import subprocess, os, json,re
        url = 'jbdc:oracle:thin:@192.168.1.114:1521:ORACLE82'
        user = 'zjhis'
        pwd = 'dec456'
        curdir = os.path.split(os.path.realpath(__file__))[0]
        cmd = '"{}/../jre1.2/bin/java.exe" -classpath "{}/../oracle";"{}/../oracle/classes12.zip" OracleCon {} {} {} "{}"' \
            .format(curdir, curdir, curdir, url, user, pwd, sql)
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = p.communicate()
       
        try:
            output = eval(str(stdout,encoding="GB18030"))
        except Exception as e:
            print('warning oracle select failed',e)
            output = []
        return output 
