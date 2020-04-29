# coding:utf-8

# 图数据和nodes.json的值定义存在冲突
# 书写办法，在compat_error.json中
# 对于每一条dict类型的子项目，type表示nodes.json定义中期望的类型
# value 表示在图数据中出现的类型
# 如：
# ...
# "type": "Int"
# "value": "point1"
# ...

# 表示，在nodes.json中期望此值是int类型，
# 而在graph文件中，出现的却是string类型的"point1"
# 这时，转换规则添加如下项, key是nodes.json期待的类型，func是转换函数
# "Int": func(x)
# ...
# 这里的func(x) 要能将"point1"转换为一个合理的整数
# def convertToInt(val):
#     if val == "point1":
#         return 1
#     elif val == "point2":
#         return 2

# 则规则就是：
# convertRules = {
#     "Int": convertToInt
# }


# 把不符合整数格式的节点数值都转换为123
# 把不符合字符串格式的节点都转换为“abc“
convertRule = {
    'Int': lambda x: 123,
    'String': lambda x: 'abc'
}
