# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by LiQing.
contact blacknepia@dingtail.com for more information
"""
import sys
import time
import threading
import traceback

from runtime.ActionIO import DataCore
from runtime.ActionIO import ActionIO


class Node(object):
    def __init__(self):
        self.io = None
        self.event_actions = {}
        self.event_links = {}
        self.no_event_prelinks = {}

    def init(self, io, event_actions, event_links, no_event_prelinks):
        self.io = io
        self.event_actions = event_actions
        self.event_links = event_links
        self.no_event_prelinks = no_event_prelinks

    def get_event_action(self, event):
        return self.event_actions[event]

    def get_event_link(self, event):
        return self.event_links[event]

    def get_no_event_prelinks(self):
        return self.no_event_prelinks


class NodeGraph(object):

    def __init__(self, action_manager, pipe_conn=None):
        self.root_nodes = []
        self.nodes = []
        self.wait_events = []
        self.action_manager = action_manager  # ActionManager()

        self.interval = 0.03
        self.command = None
        self.break_points = []
        self.pipe_conn = pipe_conn

        self.ignore = False

        if self.pipe_conn:
            self.thread_ = threading.Thread(target=self.read_pipe_data)
            self.thread_.setDaemon(True)
            self.thread_.start()

    def read_pipe_data(self):
        while True:
            self.command = self.pipe_conn.recv()
            # print(self.command)

            if isinstance(self.command, float):
                self.interval = self.command or 0.03

            if isinstance(self.command, list):
                self.break_points = self.command

    def init_with_config(self, graph_config, input_args):

        nodes_config = graph_config['nodes']

        data_core = DataCore()
        data_core.init_runtime(graph_config['runtime_data'])
        data_core.set_external_args(input_args)

        nodes = self.nodes = []  # 空列表
        for index, node_config in enumerate(nodes_config):  # 依次获取每个节点下标和每个节点内容
            io = ActionIO(data_core, index, node_config['inputs'], node_config['outputs'], self.push_event)
            event_actions = node_config['event_actions']
            event_links = node_config['event_links']
            no_event_prelinks = node_config['no_event_prelinks']
            node = Node()
            node.init(io, event_actions, event_links, no_event_prelinks)
            nodes.append(node)

        roots = graph_config['roots']
        self.root_nodes = roots

    def start(self):
        for node_idx in self.root_nodes:
            self.execute(node_idx, 'Default')

    def execute(self, node_idx, event):
        time.sleep(self.interval)  # 间隔时间
        node = self.nodes[node_idx]
        action = node.get_event_action(event)

        while self.command == 'pause':
            time.sleep(0.1)
            if self.command == 'resume':
                self.command = None
                break

        args = node.io.get_inputs()
        if self.pipe_conn:
            self.pipe_conn.send(args['node_index'])

        # self.action_manager.execute_action(action, args, node.io)
        try:
            self.action_manager.execute_action(action, args, node.io)
            time.sleep(self.interval)  # 最后节点才会执行
        except Exception as e:
            if not self.ignore:
                self.ignore = True
                if self.pipe_conn:
                    args.update({'exception': 1})
                    self.pipe_conn.send(args)
                # exc_type, exc_value, exc_tb = sys.exc_info()
                # traceback.print_exception(exc_type, exc_value, exc_tb)
            raise

    def pull_pre_no_event(self, node_idx):
        node = self.nodes[node_idx]

        for pre_index, null_event in node.get_no_event_prelinks().items():
            self.pull_pre_no_event(pre_index)  # 递归所有无in的前节点
            self.execute(pre_index, null_event)

    def push_event(self, node_idx, event):
        node = self.nodes[node_idx]


        if node.io.get_inputs().get('node_index') in self.break_points or self.command == 'step over':
            if self.pipe_conn:
                inputs = node.io.get_inputs()
                outputs = node.io.outputs
                inputs.update(outputs)
                self.pipe_conn.send(inputs)

            if self.command == 'step over':
                self.command = None

            while True:
                time.sleep(0.1)  # 断点阻塞
                if self.command in ['resume', 'step over']:
                    self.command = None
                    break

        for n_index, n_event in node.get_event_link(event).items():
            self.pull_pre_no_event(n_index)  # 前节点，无in事件
            self.execute(n_index, n_event)


class ActionManager(object):

    def __init__(self):
        self.action_map = {}
        self.scan_action_map()

    def scan_action_map(self):
        import inspect
        from runtime.Action import Action
        all_actions = {}
        exec("from actions import *", all_actions, all_actions)
        predicate = lambda member: inspect.isclass(member) and issubclass(member, Action) and member is not Action
        self.action_map.update(
            (action_name, action()) for action_name, action in all_actions.items() if predicate(action))

    # 数据的传输
    def execute_action(self, action_name, args, io):
        self.action_map[action_name](args, io)


class GraphRunnerInstance(object):

    def __init__(self, pipe_conn=None):
        self.action_manager = ActionManager()
        self.pipe_conn = pipe_conn
        self.node_graphs = []

    def run_graph(self, graph_config, input_args):
        node_graph = NodeGraph(self.action_manager, self.pipe_conn)
        node_graph.init_with_config(graph_config, input_args)
        node_graph.start()
        self.node_graphs.append(node_graph)


if __name__ == '__main__':
    instance = GraphRunnerInstance()
    print(instance.action_manager.action_map)
