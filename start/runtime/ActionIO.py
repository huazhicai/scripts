# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by LiQing.
contact blacknepia@dingtail.com for more information
"""
from copy import deepcopy


class DataCore(object):
    def __init__(self):
        self.node_data = {}
        self.runtime_data = []
        self.external_args = {}

    def init_runtime(self, runtime):
        self.runtime_data = deepcopy(runtime)  # runtime_data

    def set_external_args(self, external_args):
        self.external_args = external_args or {}

    def get_external_var(self, key):
        return self.external_args.get(key)

    def set_runtime_data(self, key, value):
        self.runtime_data[key] = value

    def get_runtime_data(self, item):
        return self.runtime_data[item]

    def set_node_data(self, node_index, key, value):
        if node_index not in self.node_data:
            self.node_data[node_index] = {}
        self.node_data[node_index][key] = value

    def get_node_data(self, nodeIndex, key):
        return self.node_data.get(nodeIndex, {}).get(key)


class ActionIO(object):

    def __init__(self, data_core, node_index, input_args, output_args, event_push):
        self._node_index = node_index  # 节点下标
        self._data_core = data_core  # deepcopy(runtime_data) 参数数据
        self._input_args = input_args
        self._output_args = output_args
        self._event_push = event_push

        self.outputs = {}

    def get_input(self, arg_name):
        return self._data_core.get_runtime_data([self._input_args[arg_name]])

    def get_inputs(self):
        return dict((name, self._data_core.get_runtime_data(index)) for name, index in self._input_args.items())

    def set_data_record(self, record, value):
        self._data_core.set_node_data(self._node_index, record, value)

    def set_output(self, output, value):
        self._data_core.set_runtime_data(self._output_args[output], value)

        self.outputs.update({output: value})  # 输出参数

    def push_event(self, event_name):
        # 传入节点下标，和‘Out’
        self._event_push(self._node_index, event_name)
        self.outputs.clear()

    def get_external_var(self, key):
        return self._data_core.get_external_var(key)
