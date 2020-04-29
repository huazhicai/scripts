# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by LiQing.
contact blacknepia@dingtail.com for more information
数据简单清洗过程
"""
from runtime.Action import Action
import numpy as np


class ReExtract(Action):
    """正则获取指定元素"""
    _id = 'd51b409e-e967-11e9-a27a-8cec4bd887f3'
    node_info = {"args": [['string_str', 'String', 'ce693d4e-f3a7-11e9-8adf-8cec4bd887f3'],
                          ['re_pattern_str', 'String', 'ce693d4f-f3a7-11e9-823e-8cec4bd887f3'],
                          ['In', 'Event', '5e3db0b4-1a56-11ea-b4b9-8cec4bd887f3']],
                 "returns": [['result_str', 'String', 'ce693d51-f3a7-11e9-bfbe-8cec4bd887f3'],
                             ['result_list', 'List', '7e6a4e98-1a5c-11ea-ac4f-8cec4bd887f3'],
                             ['Out', 'Event', 'ce693d52-f3a7-11e9-98f4-8cec4bd887f3']]}

    def __call__(self, args, io):
        import re
        obj = args['string_str']
        rule = args['re_pattern_str']
        result = re.findall(rule, obj)
        io.set_output('result_list', result)
        result_str = ''.join(result)
        io.set_output('result_str', result_str)
        io.push_event('Out')


class IterationJoint(Action):
    """遍历列表，拼接字符串"""
    _id = 'dc32ecb6-e967-11e9-9dab-8cec4bd887f3'
    node_info = {"args": [['prefix_str', 'String', 'ce693d53-f3a7-11e9-9801-8cec4bd887f3'],
                          ['suffix_list', 'List', 'ce693d54-f3a7-11e9-a29c-8cec4bd887f3'],
                          ['return_type', 'Any', 'ce693d55-f3a7-11e9-bf99-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d56-f3a7-11e9-a80a-8cec4bd887f3']],
                 "returns": [['url_list', 'List', '285744b9-4f47-498b-873e-993df96884ba'],
                             ['Out1', 'Event', 'ce693d58-f3a7-11e9-bb19-8cec4bd887f3'],
                             ['url_str', 'String', 'ce693d59-f3a7-11e9-beac-8cec4bd887f3'],
                             ['Out2', 'Event', 'ce693d5a-f3a7-11e9-ac0e-8cec4bd887f3']
                             ]}

    def __call__(self, args, io):
        prefix = args['prefix_str']
        suffix_list = args['suffix_list']
        return_type = args['return_type']
        if return_type == 'list':
            url_list = []
            for suffix in suffix_list:
                string = str(prefix) + str(suffix)
                url_list.append(string)

            io.set_output('url_list', url_list)
            io.push_event('Out1')
        else:
            for suffix in suffix_list:
                url = str(prefix) + str(suffix)
                io.set_output('url_str', url)
                io.push_event('Out2')


class ListIndex(Action):
    """选取列表中直接下表元素"""
    _id = 'e4c44b9e-e967-11e9-a109-8cec4bd887f3'
    node_info = {"args": [['index_str', 'String', '2dc0be82-7fc8-439b-a675-6ed2f2c940c0'],
                          ['result_list', 'List', '0c687d8e-0a7d-4ee9-8b3b-f33aabc2b14e'],
                          ['In', 'Event', '964b1f74-0044-11ea-82c1-8cec4bd83f9f']],
                 "returns": [['result_any', 'Any', 'efaf417f-ac7c-4d4e-b187-a809034d27cb'],
                             ['Out', 'Event', '48a26fd9-2c84-4ca7-890b-0ef6e035450a']]}

    def __call__(self, args, io):
        index = args['index_str']
        result_list = args['result_list']
        result_any = result_list[int(index)]
        io.set_output('result_any', result_any)
        io.push_event('Out')


class TupleIndex(Action):
    """选取列表中直接下表元素"""
    _id = '6aa45c8a-11a2-11ea-8c9f-8cec4bd887f3'
    node_info = {"args": [['index_str', 'String', 'b58d12fa-11a2-11ea-bf8e-8cec4bd887f3'],
                          ['result_tuple', 'Tuple', 'b5d874d2-11a2-11ea-8fe2-8cec4bd887f3'],
                          ['In', 'Event', 'b60d488c-11a2-11ea-80ef-8cec4bd887f3']],
                 "returns": [['result_any', 'Any', 'c4a0f176-11a2-11ea-bd41-8cec4bd887f3'],
                             ['Out', 'Event', 'c52f775e-11a2-11ea-aade-8cec4bd887f3']]}

    def __call__(self, args, io):
        index = args['index_str']
        Tuple = args['result_tuple']
        result_any = Tuple[int(index)]
        io.set_output('result_any', result_any)
        io.push_event('Out')


class ComposeTuple(Action):
    """选取列表中直接下表元素"""
    _id = '6aa45c8a-11a2-11ea-8c9f-8cec4bdjk3f3'
    node_info = {"args": [['value1', 'String', 'b58d12fa-11a2-11ea-bf8e-8cec4cf437f3'],
                          ['value2', 'String', 'b5d874d2-11a2-11ea-7gc2-8cec445287f3'],
                          ['value3', 'String', 'b5d874d2-11a2-11ea-7ak2-8cec4bd667f3'],
                          ['value4', 'String', 'b5d874d2-11a2-11ea-7gc2-8cec4bd887f3'],
                          ['value5', 'Any', 'b5d874d2-11a2-11ea-6542-8cec4bd667f3'],
                          ['value6', 'Int', 'b5d874d2-11a2-11ea-6542-8c6521d667f3'],
                          ['In', 'Event', 'b60d488c-11a2-11ea-45jf-8cec4bd547f3']],
                 "returns": [['tuple_value', 'Tuple', 'c4a0f176-11a2-22ca-bd41-8cec4bd887f3'],
                             ['Out', 'Event', 'c52f775e-11a2-11ea-aade-8cec4bdac5f3']]}

    def __call__(self, args, io):
        value1 = args['value1']
        value2 = args['value2']
        value3 = args['value3']
        value4 = args['value4']
        value5 = args['value5']
        value6 = args['value6']
        io.set_output('tuple_value', (value1, value2, value3, value4, value5, value6))
        io.push_event('Out')


class SplitString(Action):
    """ 按指定字符切割字符串并获取指定区间"""
    _id = 'e9976b6c-e967-11e9-a6e4-8cec4bd887f3'
    node_info = {"args": [['response', 'String', 'fbfedc78-acd1-4eca-a15d-693a1155773b'],
                          ['split_str', 'String', 'f7158ba3-ff3c-4ee8-9b88-b5bbd55aa482'],
                          ['start_index', 'String', 'edbba0cb-58b5-4f27-8eab-d68d483436fb'],
                          ['end_index', 'String', '7327158d-f95b-4c48-8605-f2f4e07e4099'],
                          ['In', 'Event', '9b0964dd-aa2c-4fbd-b9bf-68ab726ef2f1']],
                 "returns": [['result', 'List', '65ffbf96-70c6-4cfc-9b16-66c6104de43d'],
                             ['Out', 'Event', '7e3a00d9-70eb-481e-b725-cbd8cc12d161']]}

    def __call__(self, args, io):
        string = args['response']
        need_split = args['split']
        start_index = args['start_index']
        end_index = args['end_index']

        if not end_index and start_index:
            result_split = string.split(need_split)[int(start_index):]
        elif not start_index and end_index:
            result_split = string.split(need_split)[:int(end_index)]
        elif not end_index and not start_index:
            result_split = string.split(need_split)
        else:
            result_split = string.split(need_split)[int(start_index):int(end_index)]

        io.set_output('result', result_split)
        io.push_event('Out')


class StripString(Action):
    """删除字符串中指定元素"""
    _id = 'f15518f0-e967-11e9-bb56-8cec4bd887f3'
    node_info = {"args": [['response_str', 'String', 'ce693d67-f3a7-11e9-ad41-8cec4bd887f3'],
                          ['strip_str', 'String', 'ce693d68-f3a7-11e9-89d7-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d69-f3a7-11e9-a7a2-8cec4bd887f3']],
                 "returns": [['result_str', 'String', 'ce693d6a-f3a7-11e9-b25c-8cec4bd887f3'],
                             ['Out', 'Event', 'ce693d6b-f3a7-11e9-8fa5-8cec4bd887f3']]}

    def __call__(self, args, io):
        string = args['response_str']
        need_strip = args['strip_str']
        result_strip = string.strip(need_strip)
        io.set_output('result_str', result_strip)
        io.push_event('Out')


class AddDict(Action):
    """ 向字典中添加键值对"""
    _id = 'f5a77602-e967-11e9-8b5f-8cec4bd887f3'
    node_info = {"args": [['key', 'Any', '698734jc-0044-11ea-9ed2-8cec4bd83f9f'],
                          ['value', 'Any', '8dc0bec6-0044-11ea-bd92-8cec4bd83f9f'],
                          ['doc', 'Dict', 'bc7e59f6-0044-11ea-a1ee-8cec4bd83f9f'],
                          ['In', 'Event', 'ce693d6f-f3a7-11e9-99fa-8cec4bd887f3']],
                 "returns": [['result', 'Dict', 'cdb030da-0044-11ea-94db-8cec4bd83f9f'],
                             ['Out', 'Event', 'dde6c16e-0044-11ea-9ccb-8cec4bd83f9f']]}

    def __call__(self, args, io):
        key = args['key']
        value = args['value']
        dic = args['doc']
        dic[key] = value
        io.set_output('result', dic)
        io.push_event('Out')


class ApendList(Action):
    _id = 'f5a77602-e967-11e9-8b5f-8af8abd247f3'
    node_info = {"args": [['doc', 'List', '6987298c-651a-11ea-9ed2-8cec4bd83f9f'],
                          ['value', 'Any', '8dc0bec6-0851-11ea-bd92-8ce65av83f9f'],
                          ['In', 'Event', 'ce693d6f-f3a7-11e9-65ca-8cec4bd887f3']],
                 "returns": [['result', 'List', 'cdb030da-3544-52aa-94db-8cec4bd83f9f'],
                             ['Out', 'Event', 'dde6c16e-0044-96ka-9ccb-8ce328d83f9f']]}

    def __call__(self, args, io):
        doc = args['doc'] or []
        value = args['value']
        doc.append(value)
        # print(doc)
        io.set_output('result', doc)
        io.push_event('Out')


class ListData(Action):
    _id = 'f5a77602-e967-11e9-8b5f-8af8abyzv2f3'
    node_info = {"args": [['Arry', 'List', '6987298c-651a-11ea-9ed2-87654jd83f9f'],
                          ['In', 'Event', 'ce693d6f-f3a7-11e9-65ca-8cecabkc87f3']],
                 "returns": [['Value', 'List', 'cdb030da-3544-52aa-94db-8cecjka53f9f'],
                             ['Out', 'Event', 'dde6c16e-0044-96ka-9ccb-8ce32546v9f']]}

    def __call__(self, args, io):
        Arry = args['Arry']
        io.set_output('Value', Arry)
        io.push_event('Out')


class DefaultDict(Action):
    """ 向字典中添加键值对"""
    _id = 'f5a77602-e967-11e9-8b5f-8afe4bd847f3'
    node_info = {"args": [['key', 'Any', '6987298c-0044-11ea-995k-8cec4bd83f9f'],
                          ['value', 'Any', '8dc0bec6-0044-11ea-23c2-8ce65av83f9f'],
                          ['factory_func', 'String', 'bc7e59f6-0324-11ea-a1ee-8cec4bd83f9f'],
                          ['In', 'Event', 'ce693d6f-f3a7-11e9-98aa-8cec4bd887f3']],
                 "returns": [['result', 'Dict', 'cdb030da-3544-11ea-94db-8cec4bd83f9f'],
                             ['Out', 'Event', 'dde6c16e-0044-11ea-9ccb-8ce328d83f9f']]}

    def __call__(self, args, io):
        from collections import defaultdict
        key = args['key']
        value = args['value']
        factory_func = args['factory_func']
        default_dic = defaultdict(eval(factory_func))
        if factory_func == 'list':
            default_dic[key].append(value)

        io.set_output('result', default_dic)
        io.push_event('Out')


class AddingDict(Action):
    """字典相加"""
    _id = 'ff705a30-e967-11e9-afb9-8cec4bd887f3'
    node_info = {"args": [['doc1', 'Dict', 'd70845d0-ffa7-11e9-8494-42a5ef45c2c9'],
                          ['doc2', 'Dict', 'f94fccec-ffa7-11e9-b356-42a6kf45c2c9'],
                          ['In', 'Event', 'ce693d74-f3a7-11e9-a4ce-8cec4bd887f3']],
                 "returns": [['result', 'Dict', 'f94fccec-ffa7-11e9-b356-42a5ef45c2c9'],
                             ['Out', 'Event', '6c13347e-ffc4-11e9-bece-42a5ef45c2c9']]}

    def __call__(self, args, io):
        dict_one = args['doc1'] or {}
        dict_two = args['doc2']
        dict_one.update(dict_two)
        io.set_output('result', dict_one)
        io.push_event('Out')


class JointDict(Action):
    """组成字典"""
    _id = '0634379c-e968-11e9-b579-8cec4bd887f3'
    node_info = {"args": [['key_any', 'Any', 'ce696462-f3a7-11e9-b0a7-8cec4bd887f3'],
                          ['value_any', 'Any', 'ce696463-f3a7-11e9-9f33-8cec4bd887f3'],
                          ['In', 'Event', 'ce696464-f3a7-11e9-a613-8cec4bd887f3']],
                 "returns": [['result_dict', 'Dict', 'ce696465-f3a7-11e9-b7e5-8cec4bd887f3'],
                             ['Out', 'Event', 'ce696466-f3a7-11e9-ac5e-8cec4bd887f3']]}

    def __call__(self, args, io):
        key = args['key_any']
        value = args['value_any']
        dic = {}
        dic[key] = value
        io.set_output('result_dict', dic)
        io.push_event('Out')


class MergeDict(Action):
    """两个字典合并，"""
    _id = '0b4e0ad8-e968-11e9-bd14-8cec4bd887f3'
    node_info = {"args": [['doc1_dict', 'Dict', 'ce696467-f3a7-11e9-a604-8cec4bd887f3'],
                          ['doc2_dict', 'Dict', 'ea0589cb-9fa9-4b5a-b6e7-df3b3afdbbb1'],
                          ['In', 'Event', 'ce696468-f3a7-11e9-932e-8cec4bd887f3']],
                 "returns": [['result_dict', 'Dict', 'ce696469-f3a7-11e9-82cb-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69646a-f3a7-11e9-8e30-8cec4bd887f3']]}

    def __call__(self, args, io):
        dict_one = args['doc1_dict']
        for Key, Value in args['doc2_dict'].items():
            if Key not in dict_one:
                dict_one[Key] = Value
        io.set_output('result_dict', dict_one)
        io.push_event('Out')


class GetValueDict(Action):
    """已知Key  从字典中获取Value"""
    _id = '12166c3a-e968-11e9-a718-8cec4bd887f3'
    node_info = {"args": [['doc_dict', 'Dict', 'ce69646b-f3a7-11e9-bb86-8cec4bd887f3'],
                          ['key', 'String', 'ce69646b-f3a7-11e9-bb64-8cec4bd337f3'],
                          ['key_int', 'Int', '1235687-f3a7-11e9-bb64-8cec4bd337f3'],
                          ['In', 'Event', 'ce69646c-f3a7-11e9-9703-8cec4bd887f3']],
                 "returns": [['value', 'Any', 'ce69646d-f3a7-11e9-906e-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69646e-f3a7-11e9-b7b0-8cec4bd887f3']]}

    def __call__(self, args, io):
        dic = args['doc_dict']
        key = args['key']
        key_int = args['key_int']
        if key_int:
          io.set_output('value', dic[key_int])
        elif key:
          io.set_output('value', dic[key])
        io.push_event('Out')


class CleaningList(Action):
    """去除字典中value[value为列表]中的 \t \n,"""
    _id = '91f5ecd4-e9a3-11e9-9b9e-f416630aacec'
    node_info = {"args": [['doc_dict', 'Dict', 'ce69646f-f3a7-11e9-8b6d-8cec4bd887f3'],
                          ['In', 'Event', 'ce696470-f3a7-11e9-8f29-8cec4bd887f3']],
                 "returns": [['result_dict', 'Dict', 'ce696471-f3a7-11e9-a107-8cec4bd887f3'],
                             ['Out', 'Event', 'ce696472-f3a7-11e9-a81c-8cec4bd887f3']]}

    def __call__(self, args, io):
        dic = args['doc_dict']
        for key, value in dic.items():
            value = ''.join(value)
            value = ' '.join(value.split())
            dic[key] = value
        io.set_output('result_dict', dic)
        io.push_event('Out')


class FillUpInfor(Action):
    """当dict中value为空时，补充信息"""
    _id = '7c429c80-e9a3-11e9-962f-f416630aacec'
    node_info = {"args": [['doc_dict', 'Dict', 'ce696473-f3a7-11e9-ae32-8cec4bd887f3'],
                          ['In', 'Event', 'ce696474-f3a7-11e9-b0b9-8cec4bd887f3']],
                 "returns": [['result_dict', 'Dict', 'ce696475-f3a7-11e9-9eea-8cec4bd887f3'],
                             ['Out', 'Event', 'ce696476-f3a7-11e9-ac67-8cec4bd887f3']]}

    def __call__(self, args, io):
        dic = args['doc_dict']
        for key, vule in dic.items():
            if len(vule) == 0:
                dic[key] = '信息不详'
        io.set_output('result_dict', dic)
        io.push_event('Out')


class InterceptionText(Action):
    """
    如果多个字段在一个标签中，用正则截取多个字段，对内容的提取
    对value中字符串进行正则匹配
    """
    _id = '19bd24ee-e968-11e9-b671-8cec4bd887f3'
    node_info = {"args": [['doc1_dict', 'Dict', 'ce696477-f3a7-11e9-96f6-8cec4bd887f3'],
                          ['doc2_dict', 'Dict', 'ce696478-f3a7-11e9-ba2d-8cec4bd887f3'],
                          ['In', 'Event', 'ce696479-f3a7-11e9-95c0-8cec4bd887f3']],
                 "returns": [['result_dict', 'Dict', 'ce69647a-f3a7-11e9-ade2-8cec4bd887f3'],
                             ['Out', 'Event', 'ce69647b-f3a7-11e9-9ce6-8cec4bd887f3']]}

    def __call__(self, args, io):
        import re
        dic = args['doc1_dict']
        rule_dict = args['doc2_dict']
        for key, value in rule_dict.items():
            if key in dic.keys():
                con = re.findall(value, dic[key])
                con = ''.join(con).strip(' ')
                dic[key] = con

        io.set_output('result_dict', dic)
        io.push_event('Out')


class StringContact(Action):
    _id = '321dfffa-e968-11e9-b5c3-8cec4bd887f3'
    node_info = {"args": [['prefix_str', 'String', 'ce69647c-f3a7-11e9-a691-8cec4bd887f3'],
                          ['suffix_str', 'String', 'ce69647d-f3a7-11e9-9c70-8cec4bd887f3'],
                          ['In', 'Event', 'ce69647e-f3a7-11e9-bc2f-8cec4bd887f3']],
                 "returns": [['contacted_str', 'String', 'ce69647f-f3a7-11e9-b1e6-8cec4bd887f3'],
                             ['Out', 'Event', 'ce696480-f3a7-11e9-b813-8cec4bd887f3']]}

    def __call__(self, args, io):
        prefix = args['prefix_str']
        suffix = args['suffix_str']
        string = ''.join([prefix, suffix])
        io.set_output('contacted_str', string)
        io.push_event('Out')


class GetExternalVarStr(Action):
    _id = 'aa739124-289e-452d-a593-485ed88d3206'
    node_info = {"args": [['key_str', 'String', 'e1e73e20-ee99-4a04-b72f-1ae6f62ad6b8'],
                          ['In', 'Event', 'c6d71d22-e008-4621-a455-5516ab2a5c4d']],
                 "returns": [['value_str', 'String', 'b90006b6-f97a-49d7-8259-98b2f09bde2f'],
                             ]}

    def __call__(self, args, io):
        key = args['key_str']
        value = io.get_external_var(key)
        io.set_output('value_str', str(value))


class CumulativeDcit(Action):
    """字典的累加"""
    _id = '8232d950-f4aa-11e9-83ab-8cec4bd887f3'
    node_info = {"args": [['doc_dict', 'Dict', 'a30a9d5c-f4aa-11e9-956e-8cec4bd887f3'],
                          ['finish_signal_str', 'String', '56833196-f4ad-11e9-87ce-8cec4bd887f3'],

                          ['In', 'Event', 'a30a9d5d-f4aa-11e9-a1f2-8cec4bd887f3']],
                 "returns": [['dict_new', 'Dict', 'a30a9d5e-f4aa-11e9-afd5-8cec4bd887f3'],
                             ['Out', 'Event', 'a30a9d5f-f4aa-11e9-8c68-8cec4bd887f3']]}

    dict_all = {}

    def __call__(self, args, io):
        dict_one = args['doc_dict']
        finish_signal = args['finish_signal_str']
        self.dict_all = dict_one.update(self.dict_all)

        if finish_signal:
            """当url为最后一个时候，字典累加完成，节点向后输出"""
            io.set_output('dict_new', self.dict_all)
            io.push_event('Out')


class AddingList(Action):
    """列表相加"""
    _id = '04966ce4-fbc0-11e9-b67d-8cec4bd887f3'
    node_info = {"args": [['doc1_list', 'List', 'ebf269b0-0050-11ea-b2e3-8cec4bd83f9f'],
                          ['doc2_list', 'List', 'ebf269b1-0050-11ea-a615-8cec4bd83f9f'],
                          ['In', 'Event', 'ebf269b2-0050-11ea-9fd6-8cec4bd83f9f']],
                 "returns": [['result_list', 'List', 'ebf269b3-0050-11ea-a06d-8cec4bd83f9f'],
                             ['Out', 'Event', 'ebf269b4-0050-11ea-b010-8cec4bd83f9f']]}

    def __call__(self, args, io):
        list_one = args['doc1_list']
        list_two = args['doc2_list']
        new_list = list_one + list_two
        io.set_output('result_list', new_list)
        io.push_event('Out')


class ListFetch(Action):
    '''取列表指定下表元素'''
    _id = '04966ce4-fbc0-11e9-b67d-8cec4bd00000'
    node_info = {"args": [['input_list', 'List', '2c331de0-8e24-4f88-aba8-c5b85bf620f9'],
                          ['index_int', 'Int', 'be723dbf-0053-11ea-b7e0-8cec4bd83f9f'],
                          ['In', 'Event', 'be723dc0-0053-11ea-b171-8cec4bd83f9f']],
                 "returns": [['result_any', 'Any', 'be723dc1-0053-11ea-96d4-8cec4bd83f9f'],
                             ['Out', 'Event', 'be723dc2-0053-11ea-835b-8cec4bd83f9f']]}

    def __call__(self, args, io):
        list_in = args['input_list']
        index = args['index_int']
        io.set_output('result_any', list_in[index])
        io.push_event('Out')


class StrListJoin(Action):
    _id = '61c891f1-55df-4d31-8d49-de18489a0413'
    node_info = {"args": [['prefix_str', 'String', 'fc168ab4-0073-11ea-bedc-8cec4bd83f9f'],
                          ['input_list', 'List', 'fc168ab5-0073-11ea-8314-8cec4bd83f9f'],
                          ['div_str', 'String', 'fc168ab6-0073-11ea-9da5-8cec4bd83f9f'],
                          ['subfix_str', 'String', 'fc168ab7-0073-11ea-a467-8cec4bd83f9f'],
                          ['In', 'Event', 'fc168ab8-0073-11ea-ac91-8cec4bd83f9f']],
                 "returns": [['string_out', 'Any', 'fc168ab9-0073-11ea-9a32-8cec4bd83f9f'],
                             ['Out', 'Event', 'fc168aba-0073-11ea-9bad-8cec4bd83f9f']]}

    def __call__(self, args, io):
        prefix = args['prefix_str'] or ''
        list_in = args['input_list']
        div_char = args['div_str'] or ''
        subfix = args['subfix_str'] or ''
        io.set_output('string_out', prefix + div_char.join(list_in) + subfix)
        io.push_event('Out')


class SpaceStrip(Action):
    """字符串去除空格"""
    _id = 'd0c1dbc8-0458-11ea-b416-8cec4bd887f3'
    node_info = {"args": [['receive_str', 'String', 'ff78e9cc-0458-11ea-92ac-8cec4bd887f3'],
                          ['In', 'Event', '28a451a8-0459-11ea-9f13-8cec4bd887f3']],
                 "returns": [['ws_str', 'String', '2dbe92f8-0459-11ea-a403-8cec4bd887f3'],
                             ['start_str', 'String', '46164a28-0459-11ea-9691-8cec4bd887f3'],
                             ['end_str', 'String', '4ba324cc-0459-11ea-a54b-8cec4bd887f3'],
                             ['all_str', 'String', '5117bcb6-0459-11ea-810e-8cec4bd887f3'],
                             ['Out', 'Event', '59bf3642-0459-11ea-9c8e-8cec4bd887f3']]}

    def __call__(self, args, io):
        receive_str = args['receive_str']
        # 去除前后空格的
        ws_str = receive_str.strip()
        # 去除开头空格
        start_str = receive_str.lstrip()
        # 去除结尾空格
        end_str = receive_str.rstrip()
        all_str = receive_str.replace(" ", "")
        io.set_output('ws_str', ws_str)
        io.set_output('start_str', start_str)
        io.set_output('end_str', end_str)
        io.set_output('all_str', all_str)
        io.push_event('Out')


class Carve_List(Action):
    '''将列表 按照指定等分，切割'''
    _id = '63f8ee34-1658-11ea-94a9-8cec4bd887f3'
    node_info = {"args": [['receive_list', 'List', '649fd286-1658-11ea-ab70-8cec4bd887f3'],
                          ['list_elements', 'String', '64fed8d8-1658-11ea-8b73-8cec4bd887f3'],
                          ['In', 'Event', '655fba74-1658-11ea-8fb9-8cec4bd887f3']],
                 "returns": [['subset_list', 'List', '65b6c34a-1658-11ea-874a-8cec4bd887f3'],
                             ['Out', 'Event', '798e6e74-1658-11ea-a094-8cec4bd887f3']]}

    def __call__(self, args, io):
        receive_list = args['receive_list']
        list_elements = args['list_elements']
        several = len(receive_list) // int(list_elements)
        for subset_list in np.array_split(receive_list, several):
            io.set_output('subset_list', list(subset_list))
            io.push_event('Out')


class TypeConversion(Action):
    '''数据类型Type转换'''
    _id = '5bac5a1e-1afa-11ea-a994-8cec4bd887f3'
    node_info = {"args": [['receive_data', 'Any', 'e6b8a492-1b0f-11ea-b2c1-8cec4bd887f3'],
                          ['In', 'Event', 'e70b0c8a-1b0f-11ea-8423-8cec4bd887f3']],
                 "returns": [['int_data', 'Int', 'e756fcd4-1b0f-11ea-86ae-8cec4bd887f3'],
                             ['str_data', 'String', 'e7975c3a-1b0f-11ea-a87e-8cec4bd887f3'],
                             ['list_data', 'List', 'e7c30268-1b0f-11ea-81d4-8cec4bd887f3'],
                             ['tuple_data', 'Tuple', 'e7fc275c-1b0f-11ea-81fd-8cec4bd887f3'],
                             ['Out', 'Event', 'e809b2a2-1b0f-11ea-9ed3-8cec4bd887f3']]}

    def __call__(self, args, io):
        receive_data = args['receive_data']

        int_data = int(receive_data)
        str_data = str(receive_data)
        # if type(receive_data) != int:
        # list_data = list(receive_data)
        # tuple_data = tuple(receive_data)
        # io.set_output('list_data', list_data)
        # io.set_output('tuple_data', tuple_data)
        io.set_output('int_data', int_data)
        io.set_output('str_data', str_data)
        io.push_event('Out')


class ByKeyMapValue(Action):
    _id = '5bac5a1e-1afa-11ea-a994-8ce8888avcf3'
    node_info = {"args": [['empty_value_dic', 'Dict', 'e6b8a492-1b0f-11ea-b2c1-8ce854261qg3'],
                          ['value_source_dic', 'Dict', 'e85421av-1b0f-11ea-b2c1-8ce854261qg3'],
                          ['In', 'Event', 'e70b0c8a-1b0f-11ea-8423-88451hac887f3']],
                 "returns": [
                     ['out_dic', 'Dict', 'e7fc275c-1b0f-11ea-81fd-48hcabd887f3'],
                     ['Out', 'Event', 'e7uavka3-1b0f-11ea-9ed3-83210bd887f3']]}

    def __call__(self, args, io):
        empty_value_dic = args['empty_value_dic']
        value_source_dic = args['value_source_dic']

        self.recursion(empty_value_dic, value_source_dic)

        io.set_output('out_dic', empty_value_dic)
        io.push_event('Out')

    def recursion(self, doc1, doc2):
        for key in doc1.keys():
            if isinstance(doc1[key], dict):
                self.recursion(doc1[key], doc2)
            # print(doc1[key])
            elif doc1[key] == '':
                doc1[key] = doc2.get(key, None)


class DispatchValue(Action):
    _id = '5bac5a1e-1afa-11ea-a994-8ce2110avcf3'
    node_info = {"args": [['A', 'Any', 'e6b8a492-1b0f-11ea-b2c1-8ce321561qg3'],
                          ['B', 'Any', 'e85421av-1b0f-11ea-b2c1-8ce85423210'],
                          ['In', 'Event', 'e70b0c8a-1b0f-11ea-32ac-88451hac887f3']],
                 "returns": [
                     ['data', 'Any', 'e7fc275c-1b0f-11ea-81fd-48hcabd82133'],
                     ['Out', 'Event', 'e7uavka3-1b0f-11ea-9ed3-8cec4bd887f3']]}

    def __call__(self, args, io):
        A = args['A']
        B = args['B']
        data = None
        if A:
            data = A
        elif B:
            data = B
        io.set_output('data', data)
        io.push_event('Out')


class DeepCopy(Action):
    _id = '5b52141e-1afa-11ea-a994-8ce2110avcf3'
    node_info = {"args": [['doc', 'Dict', 'e6b8a492-1b0f-11ea-b2c1-8ce3321546g3'],
                          ['In', 'Event', 'e70b0c8a-1b0f-11ea-32ac-12341hac887f3']],
                 "returns": [
                     ['out_dic', 'Dict', 'e72154ac-1b0f-11ea-81fd-3256cabd82133'],
                     ['Out', 'Event', 'e71241a3-1b0f-11ea-9ed3-8cec4bd887f3']]}

    def __call__(self, args, io):
        import copy
        doc = args['doc']
        out_dic = copy.deepcopy(doc)

        io.set_output('out_dic', out_dic)
        io.push_event('Out')
