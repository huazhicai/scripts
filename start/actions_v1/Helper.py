# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by liqing.
contact blacknepia@dingtail.com for more information

"""
from runtime.Action import Action
import time
import warnings

warnings.filterwarnings("ignore")


class Time(Action):
    """获取当前cpu时间"""
    _id = 'b8248ac6-156d-11ea-a61f-8cec4bd887f3'
    node_info = {"args": [['In', 'Event', 'b9cb0e6e-156d-11ea-8851-8cec4bd887f3']],
                 "returns": [['time_float', 'Float', 'ba5c5608-156d-11ea-ab22-8cec4bd887f3'],
                             ['Out', 'Event', 'bacfce5e-156d-11ea-9266-8cec4bd887f3']]}

    def __call__(self, args, io):
        times = time.clock()
        io.set_output('time_float', times)
        io.push_event('Out')


class Time_difference(Action):
    """获取时间差"""
    _id = '8ba819d2-156f-11ea-b4d5-8cec4bd887f3'
    node_info = {"args": [['start_time_float', 'Float', '8c5cd282-156f-11ea-9475-8cec4bd887f3'],
                          ['end_time_float', 'Float', '8cd33da4-156f-11ea-9e2b-8cec4bd887f3'],
                          ['In', 'Event', '8d194580-156f-11ea-a3ce-8cec4bd887f3']],
                 "returns": [['run_time_str', 'String', '8d55b936-156f-11ea-ab02-8cec4bd887f3'],
                             ['Out', 'Event', '8e5daf5c-156f-11ea-8e05-8cec4bd887f3']]}

    def __call__(self, args, io):
        start = args['start_time_float']
        end = args['end_time_float']
        run_time = str(end - start)
        io.set_output('run_time_str', run_time)
        io.push_event('Out')


class StringData(Action):
    _id = '3e449568-cdcd-45ce-9ca0-dea1ffdfaa3b'
    node_info = {
        "args": [['Set', 'String', '70930e22-6f1b-4d40-b2ac-df504bdb451f']],
        "returns": [['Value', 'String', 'dce1d461-261d-4439-9aa2-252f5e01b9d2']]
    }

    def __call__(self, args, io):
        Set = args['Set']
        io.set_output('Value', Set)


class IntData(Action):
    _id = '8005ad30-5818-4b76-801d-008b9b6513eb'
    node_info = {
        "args": [['Set', 'Int', '1b93fd9d-fd38-4c51-a082-bb82cab398ca']],
        "returns": [['Value', 'Int', '655290fa-6971-45f9-8e9f-c33621e7050f']]
    }

    def __call__(self, args, io):
        Set = args['Set']
        io.set_output('Value', Set)


class FloatData(Action):
    _id = '390e0132-f8d0-41ac-a405-496418111523'
    node_info = {
        "args": [['Set', 'Float', '81142338-411d-4c92-9e02-c2b11c8f1a9f']],
        "returns": [['Value', 'Float', '6aef1b4c-86d2-4287-a34b-207573b73bd3']]
    }

    def __call__(self, args, io):
        Set = args['Set']
        io.set_output('Value', Set)


class BoolData(Action):
    _id = '92c6d3bc-2647-4ae7-95ca-c4aa65c3c5b8'
    node_info = {
        "args": [['Set', 'Bool', 'd84983fc-1d13-4b2a-9230-c874a707c5f2']],
        "returns": [['Value', 'Bool', '6b354c55-e6b1-4c93-9e0d-9695820f4a24']]
    }

    def __call__(self, args, io):
        Set = args['Set']
        io.set_output('Value', Set)


class ArryData(Action):
    _id = 'c14909bf-172e-416f-b6e6-af673dd079d4'
    node_info = {
        "args": [['Set', 'List', 'c53cd6cd-fb18-4ca6-a94a-35f655892199']],
        "returns": [['Value', 'List', '9a35267c-a672-4107-9ef9-6a313d7f98d4']]
    }

    def __call__(self, args, io):
        Set = args['Set']
        io.set_output('Value', Set)


class DictData(Action):
    _id = 'a45da434-a733-42e2-8dde-6398109d0dd3'
    node_info = {
        "args": [['Set', 'Dict', '904b3f6d-b13c-4b05-87d0-0b16fbccfb6d']],
        "returns": [['Value', 'Dict', '65ca6888-c08e-4ffd-af43-ab05111150c0']]
    }

    def __call__(self, args, io):
        Set = args['Set']
        io.set_output('Value', Set)


class Add(Action):
    _id = '4217517a-8ab5-44f1-8d96-cbae2b23b1ff'
    node_info = {
        "args": [['A', 'Int', '4a82fdf1-0e16-402c-8f14-986abd728351'],
                 ['B', 'Int', 'c69b3328-1bd9-4196-b4cf-95006e6863f4']],
        "returns": [['Value', 'Int', '7e4bf247-6457-4026-8bd8-4686a9e5634c']]
    }

    def __call__(self, args, io):
        A = args['A']
        B = args['B']
        io.set_output('Value', A + B)


class RandomInteger(Action):
    _id = '688aefdb-b877-4bee-92f2-c2641a07bf8f'
    node_info = {
        "args": [['Min', 'Int', '04c31788-8f91-404a-a537-686067e01595'],
                 ['Max', 'Int', 'ef7f408e-6cb4-41dd-a90a-9e356b72f547']],
        "returns": [['Value', 'Int', 'c9cf46d5-6e8e-4145-8ae4-871ddd2cfa0f']]
    }

    def __call__(self, args, io):
        from random import randint
        Min = args['Min']
        Max = args['Max']
        Value = randint(Min, Max)
        io.set_output('Value', Value)


class CompareObject(Action):
    _id = 'c17f8d80-b25c-4a83-8190-7c877e9208d4'
    node_info = {
        "args": [['A', 'Any', 'bf1d46b8-2e06-4659-aebb-6caeab0079c2'],
                 ['B', 'Any', 'be4d27ad-35jv-4edd-a120-2bb5880a1d8f'],
                 ['In', 'Event', 'b60d488c-11a2-11ea-akct-8cec4bact7f3']],
        "returns": [['Equal', 'Event', 'ba762eea-230a-40f1-85f7-22d32f20593d'],
                    ['Not Equal', 'Event', 'ead958e4-a0ec-46b9-a9c7-6e606fbe4ab7']]
    }

    def __call__(self, args, io):
        A = args['A']
        B = args['B']
        if A == B:
            io.push_event('Equal')
        else:
            io.push_event('Not Equal')


class SwitchCase(Action):
    _id = 'c17f8d80-b25c-4a83-8190-7c877e9534d4'
    node_info = {
        "args": [['A', 'Any', 'bf1d46b8-2e06-4659-aebb-6caeakac39c2'],
                 ['B', 'Any', 'be4d27ad-a596-4edd-a120-2bb644ca1d8f'],
                 ['C', 'Any', 'bf1d46b8-2e06-4659-aebb-6caeakaknc32'],
                 ['D', 'Any', 'be4d27ad-a596-4edd-a120-2bb644cakc5f'],
                 ['E', 'Any', 'be4d27ad-a596-654a-a120-2bb644ca1d8f'],
                 ['F', 'Any', 'bf1d46b8-2e06-4659-45kc-6caeakaknc32'],
                 ['G', 'Any', 'be4d27ad-a596-4edd-a120-2b6542cakc5f'],
                 ['Value', 'Any', 'be4d27ad-a596-4edd-a120-2jck22cakc5f'],
                 ['In', 'Event', 'b60d488c-11a2-34jc-80ef-8cec4bact7f3']],
        "returns": [['A', 'Event', 'bf1d46b8-85jv-4659-aebb-6caeakac39c2'],
                 ['B', 'Event', 'be4d27ad-a596-4598-a120-2bb644ca1d8f'],
                 ['C', 'Event', 'bf1d46b8-2e06-ack5-aebb-6caeakaknc32'],
                 ['D', 'Event', 'be4d27ad-8jca-4edd-a120-2bb644cakc5f'],
                 ['E', 'Event', 'be4d27ad-a596-621c-a120-2bb644ca1d8f'],
                 ['F', 'Event', 'bf1d46b8-2e06-kck3-45kc-6caeakaknc32'],
                 ['G', 'Event', 'be4d27ad-a596-akc0-a120-2b6542cakc5f']]
                  }
    def __call__(self, args, io):
        A = args['A']
        B = args['B'] 
        C = args['C']   
        D = args['D']
        E = args['E']
        F = args['F']
        G = args['G']
        Value = args['Value']
        if A == Value:
            io.push_event('A')
        elif B == Value:
            io.push_event('B')
        elif C == Value:
            io.push_event("C")
        elif D == Value:
            io.push_event('D')
        elif E == Value:
            io.push_event('E')
        elif F == Value:
            io.push_event('F')
        elif G == Value:
            io.push_event('G')


class ArrayMapToDict(Action):
    _id = 'c17f8d80-b25c-4a83-8190-7c877e543974'
    node_info = {
        "args": [['keys', 'List', 'bf1d46b8-2e06-608v-aebb-6caeab0079c2'],
                 ['values', 'Any', 'be4d27ad-a596-4edd-a120-2bb5880a1d8f'],
                 ['In', 'Event', 'b60d488c-clrc-11ea-80ef-8cec4bact7f3']],
        "returns": [['doc', 'Dict', 'ba762eea-230a-40f1-ackt-22d32f20593d'],
                    ['Out', 'Event', 'e8dnc8e4-a0ec-46b9-a9c7-6e606fbe4ab7']]
    }
    def __call__(self, args, io):
        from collections import OrderedDict 

        keys = args['keys']
        values = args['values']
        doc = dict(zip(keys, values))

        io.set_output('doc', doc)
        io.push_event('Out')


class MergeBranch(Action):
    _id = 'c17f8d80-b25c-4a83-8190-7c877jdnc774'
    node_info = {
        "args": [['value1', 'Any', 'bf1d46b8-2e06-608v-aebb-6c7jv4a079c2'],
                 ['value2', 'Any', 'beuv876d-a596-4edd-a120-2bb5880a1d8f'],
                 ['In', 'Event', 'b60d488c-clrc-11ea-34nv-8cec4bact7f3']],
        "returns": [['value', 'Any', 'baajv87a-230a-40f1-ackt-22d32f20593d'],
                    ['Out', 'Event', 'e8dnc8e4-a0ec-46b9-a9c7-jjja6fbe4ab7']]
    }
    def __call__(self, args, io):

        value1 = args['value1']
        value2 = args['value2']
        if value1:
            io.set_output('value', value1)
        elif value2:
            io.set_output('value', value2)

        io.push_event('Out')