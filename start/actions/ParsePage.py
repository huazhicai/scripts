# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by LiQing.
created by LiQing
ccontact blacknepia@dingtail.com for more information
"""
from runtime.Action import Action
from lxml import html, etree
import lxml


class JsonLoads(Action):
    """将json格式转化为python字符"""
    _id = 'a1596ee2-e968-11e9-b900-8cec4bd887f3'
    node_info = {"args": [['page_source_str', 'String', 'ce698beb-f3a7-11e9-9d04-8cec4bd887f3'],
                          ['In', 'Event', 'ce698bec-f3a7-11e9-9cec-8cec4bd887f3']],
                 "returns": [['result_dict', 'Dict', 'ce698bed-f3a7-11e9-8057-8cec4bd887f3'],
                             ['Out', 'Event', 'ce698bee-f3a7-11e9-b427-8cec4bd887f3']]}

    def __call__(self, args, io):
        import json
        content = args['page_source_str']
        result = json.loads(content)
        io.set_output('result_dict', result)
        io.push_event('Out')


class ParseXpath(Action):
    """通过xpath ，获取指定字段"""
    _id = 'a968661a-e968-11e9-8902-8cec4bd887f3'
    node_info = {"args": [['page_source_str', 'String', 'ce698bef-f3a7-11e9-bee6-8cec4bd887f3'],
                          ['xpath_str', 'String', 'ce698bf0-f3a7-11e9-99bf-8cec4bd887f3'],
                          ['In', 'Event', 'ce698bf1-f3a7-11e9-90b3-8cec4bd887f3']],
                 "returns": [['result_list', 'List', 'ce698bf2-f3a7-11e9-9430-8cec4bd887f3'],
                             ['Out', 'Event', 'ce698bf3-f3a7-11e9-9c15-8cec4bd887f3']]}

    def __call__(self, args, io):
        page_source = args['page_source_str']
        #page_source = etree.fromstring(page_source)
        tree = etree.HTML(page_source)
        rule = args['xpath_str']
        result_dict = tree.xpath(rule)
        io.set_output('result_list', result_dict)
        io.push_event('Out')


class Parse_Xpath_More(Action):
    """通过xpath ，获取多个字段"""
    _id = 'afa2a5ac-e968-11e9-904e-8cec4bd887f3'
    node_info = {"args": [['page_source_str', 'String', 'ce698bf4-f3a7-11e9-a142-8cec4bd887f3'],
                          ['doc_dict', 'Dict', 'ce69b234-f3a7-11e9-8d36-8cec4bd887f3'],
                          ['In', 'Event', 'ce69b235-f3a7-11e9-bd85-8cec4bd887f3']],
                 "returns": [['result_dict', 'Dict', 'ce69b236-f3a7-11e9-9743-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69b237-f3a7-11e9-84d1-8cec4bd887f3']]}

    def __call__(self, args, io):
        page_source = args['page_source_str']
        # print(etree.tostring(page_source))
  
        if isinstance(page_source, lxml.etree._Element):
            tree = page_source
        else:
            tree = html.etree.HTML(page_source)
        rule_dict = args['doc_dict']
        result_dict = {}
        for key, value in rule_dict.items():
            values = tree.xpath(value)
            values = ''.join(values)
            result_dict[key] = ''.join(values.split())
        io.set_output('result_dict', result_dict)
        io.push_event('Out')


class Parse_Xpath_table(Action):
    '''通过xpath，解析类似table表格类的数据'''
    _id = 'f8eea3fe-04e7-11ea-b418-8cec4bd887f3'
    node_info = {"args": [['page_source_str', 'String', '41725ec2-04ec-11ea-bbd2-8cec4bd887f3'],
                          ['xpath_str', 'String', '4f466558-04ec-11ea-994d-8cec4bd887f3'],
                          ['title_xpath_dict', 'Dict', '6584f8be-04ec-11ea-980a-8cec4bd887f3'],
                          ['In', 'Event', '539bf0d8-04ec-11ea-a857-8cec4bd887f3']],
                 "returns": [['result_list', 'List', '73198600-04ec-11ea-b39c-8cec4bd887f3'],
                             ['Out', 'Event', '735ca39e-04ec-11ea-8466-8cec4bd887f3']]}

    def __call__(self, args, io):
        page_source = args['page_source_str']
        etree = html.etree
        tree = etree.HTML(page_source)
        rule = args['xpath_str']  # 最外层标签xpath,所有子集标签的父类
        result_list = tree.xpath(rule)
        list_line = []
        dict_data = {}
        list_all = []
        subset_dict = args['title_xpath_dict']
        for i in result_list:
            for key, value in subset_dict.items():
                params = i.xpath(value)
                params = ''.join(params)
                params = ''.join(params.split())
                dict_data[key] = params
                #subset_data = key + ':' + params
                #list_line.append(subset_data)
            list_all.append(dict_data)
            dict_data= {}
            list_line = []
        io.set_output('result_list', list_all)
        io.push_event('Out')


class Pagexpath(Action):
    """页面所需要xpath"""
    _id = '8ce0e1d2-f3e9-11e9-be00-8cec4bd887f3'
    node_info = {"args": [['xpath_dict', 'Dict', 'b90b3c4a-1a57-11ea-9fc1-8cec4bd887f3'],
                          ['In', 'Event', 'd577685e-10e2-11ea-9773-8cec4bd887f3']],
                 "returns": [['xpath_dict', 'Dict', 'dd7d3c58-10e2-11ea-ad3d-8cec4bd887f3'],
                             ['Out', 'Event', 'e66641b4-10e2-11ea-a1e9-8cec4bd887f3']]}

    def __call__(self, args, io):
        xpath_dict = args['xpath_dict']
        io.set_output('xpath_dict', xpath_dict)
        io.push_event('Out')
