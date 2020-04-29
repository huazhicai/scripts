# coding:utf-8


def compatable(defType, value):
    """
    检查值和类型是否兼容
    """
    if defType == 'Int':
        return type(value) == int
    elif defType == 'Float':
        return type(value) == float
    elif defType == 'Bool':
        return type(value) == bool
    elif defType == 'Dict':
        return type(value) == dict
    elif defType == 'String':
        return type(value) == str
    elif defType == 'List':
        return type(value) == list
    elif defType == 'Vec3':
        if type(value) not in [str, str]:
            return False
        from util import Vec3
        val = Vec3.valueFromString(value)
        return val != None
    elif defType == 'Any':
        return type(value) in [int, float, bool, str, list, object]
    elif defType == 'Array':
        return type(value) == list


# 根据nodes的meta文件，检查图数据的类型是否有不兼容的地方
def checkCompat(defData, graphData):
    """
    将图数据和节点定义文件的类型信息进行比对，查看有没有不兼容的地方。
    如果有，输出兼容性错误信息
    """
    nodes = graphData['nodes']
    fastDef = {}
    for defNode in defData:
        fastDef[defNode['name'][-1]] = defNode

    compatErrors = []

    for node in nodes:
        typeId = node['type']
        nodeDef = fastDef[typeId]

        args = node['args']
        for argKey, argVal in list(args.items()):
            # argKey就是SubItem的TypeId
            for argDef in nodeDef['args']:
                if argDef['name'][-1] != argKey:
                    continue

                if not compatable(argDef['type'], argVal):
                    compatErrors.append({
                        'id': node['id'],
                        'subItemTypeId': argKey,
                        'type': argDef['type'],
                        'value': argVal
                    })

    return compatErrors


def convert(graphData, compatErrors, convertRule):
    """
    将图数据中，不兼容的类型，根据compatErrors信息和给定的转换规则convertRule
    转换为新的图数据，此后才能打开
    """
    nodes = graphData['nodes']
    fastCompatErrors = {}
    for compatError in compatErrors:
        fastCompatErrors[compatError['id']] = compatError

    newNodes = []

    for node in nodes:
        if node['id'] not in fastCompatErrors:
            continue

        compatError = fastCompatErrors[node['id']]

        args = node['args']

        newArgs = {}

        for argKey, argVal in list(args.items()):
            if argKey != compatError['subItemTypeId']:
                newArgs[argKey] = argVal
                continue

            convertType = compatError['type']
            newArgs[argKey] = convertRule[convertType](argVal)

        node['args'] = newArgs


def convertFile(filename):
    """
    根据compat_error给出的错误信息，利用rules
    将filename中的图文件内容进行转换
    """
    import json
    import os, sys
    import traceback
    from ConvertRules import convertRule
    compatErrors = []
    with open('compat_error.json') as f:
        compatErrors = json.load(f)

    graphData = None
    with open(filename) as f:
        graphData = json.load(f)

    dataString = json.dumps(graphData)
    newGraphData = json.loads(dataString)

    failed = False

    try:
        convert(newGraphData, compatErrors, convertRule)
    except Exception as e:
        failed = True
        traceback.print_exc(file=sys.stderr)

    if failed:
        # 转换失败，不写文件
        return False

    # 原有的图形数据写入到一个old文件中
    parts = os.path.splitext(filename)
    oldFilename = parts[0] + '_old' + parts[1]
    with open(oldFilename, 'w') as f:
        json.dump(graphData, f, indent=4)

    # 新的图形数据覆盖原来的文件
    with open(filename, 'w') as f:
        json.dump(newGraphData, f, indent=4)

    return True


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('usage: python backcompat.py [filename]')
        sys.exit(1)

    print('converting', sys.argv[1])

    if convertFile(sys.argv[1]):
        print('convert success')
    else:
        print('convert failed')


