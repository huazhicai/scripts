import os
from subprocess import call

lst = os.listdir(os.getcwd())
os.chdir(os.getcwd())
for c in lst:
    if os.path.isfile(c) and c.endswith('.py') and c.find("to_three") == -1:  # 去掉AllTest.py文件
        print(c)
        # os.popen('2to3 -w {}'.format(c))
        # call(['2to3 -w', c])
        os.system('2to3 -w {}'.format(c))
