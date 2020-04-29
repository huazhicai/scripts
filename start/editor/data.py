# coding:utf-8
import os
from mutil import loadJsonData, dumpJsonData


def load_nodes_meta_information():
    """右键菜单模板数据"""
    return loadJsonData(os.path.join('meta', 'nodes.json'))


def load_graph_information(filename):
    return loadJsonData(filename)


def load_color_config():
    return loadJsonData(os.path.join('meta', 'colors.json'))


def load_prefs():
    return loadJsonData(os.path.join('meta', 'prefs.json'))


def save_prefs(prefs):
    dumpJsonData(os.path.join('meta', 'prefs.json'), prefs)
