"""
运行所有爬取官网数据的脚本
"""

import os

path = os.path.dirname(os.path.dirname(__file__))
lst = os.listdir(path)  # 获取path目录下所有的文件
for c in lst:
    if c.endswith('.py'):  # 判断文件名是以.py结尾的，并且去掉run.py文件
        print(c)  # 查看文件
        os.system('python {}'.format(os.path.join(path, c)))  # 执行脚本
