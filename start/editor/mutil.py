# coding: utf-8
import os, sys
import json
import logging
import logging.handlers


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    # base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    # return os.path.join(base_path, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


def loadJsonData(filename):
    """
    从文件中加载json数据
    :param filename: 文件名'meta/prefs.json'
    :return: python对象
    """
    filename = resource_path(filename)
    assert os.path.exists(filename), '%s do not exists' % filename

    data = None
    with open(filename) as f:
        data = json.load(f)

    return data


def dumpJsonData(filename, obj):
    """
    将对象写入到json文件中
    :param filename: 写入的文件名
    :param obj: 要写入json文件的对象
    """
    dataDir = os.path.split(filename)[0]
    if dataDir == '':
        dataDir = '.'
    dataDir = resource_path(dataDir)
    assert os.path.exists(dataDir), '%s directory do not exists' % dataDir

    filename = resource_path(filename)
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=4)


def pureName(filename):
    """
    去除文件名后缀的纯文件名
    :param filename: 需要去除后缀的文件名
    :return: 去除后缀后的文件名
    """
    return os.path.splitext(os.path.split(filename)[1])[0]


def simpleFileName(filename):
    """
    去除路径后的单纯文件名
    """
    return os.path.split(filename)[1]


def setUpLog(logName):
    logger = logging.getLogger(logName)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(message)s')
    logFile = '%s.log' % logName if logName != '' else 'root.log'

    fileHandler = logging.handlers.RotatingFileHandler(
        logFile,
        mode='a',
        maxBytes=(1048576 * 5),
        backupCount=7
    )
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
