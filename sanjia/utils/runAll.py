"""
运行所有爬取官网数据的脚本
"""

import os

path = '/Users/mac/PycharmProjects/shengnei/sanjia/'
lst = os.listdir(path)  # 获取当前目录下所有的文件名
for c in lst:
    if c.endswith('.py') and c.find("utils") == -1:  # 判断文件名是以.py结尾的，并且去掉run.py文件
        print(c)  # 查看文件
        os.system('python {}'.format(os.path.join(path, c)))
