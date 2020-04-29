import json
import os
from mutil import loadJsonData


class Value(object):
    def __init__(self):
        self.idx = None
        self.value = None


def validate_def_data(defData):  # nodes.json data
    uuidSet = set()
    for nodeDef in defData:
        for arg in nodeDef['args']:
            uuid = arg['name'][1]
            assert uuid not in uuidSet, 'Duplicate UUID !!! : %s' % uuid
            # assert UUID(uuid, version=4)
            uuidSet.add(uuid)

        for ret in nodeDef['returns']:
            uuid = ret['name'][1]
            assert uuid not in uuidSet, 'Duplicate UUID !!! : %s' % uuid
            # assert UUID(uuid, version=4)
            uuidSet.add(uuid)

        uuid = nodeDef['name'][1]
        assert uuid not in uuidSet, 'Duplicate UUID !!! : %s' % uuid
        # assert UUID(uuid, version=4)
        uuidSet.add(uuid)

    # NOTE: query类节点不可以使用Event
    # NOTE: 类型的首字母必须是大写
    for nodeDef in defData:
        if nodeDef.get('query', False):
            for arg in nodeDef['args']:
                assert arg['type'] != 'Event'
                assert 65 <= ord(arg['type'][0]) <= 90

            for ret in nodeDef['returns']:
                assert ret['type'] != 'Event'
                assert 65 <= ord(ret['type'][0]) <= 90

    # NOTE: 非query节点类，如果定义了event，一定要有对应的func
    for nodeDef in defData:
        if nodeDef.get('query', False):
            continue
        for arg in nodeDef['args']:
            if arg['type'] != 'Event':
                continue
            try:
                assert 'action' or 'function' in arg
            except:
                print('Def Error, event does not have func or action', nodeDef)
                raise


def validate_editor_data(editorData):
    edgeSet = set()
    for editorEdge in editorData["edges"]:
        start = editorEdge["start"]
        end = editorEdge["end"]
        startItemID = editorEdge["startItemId"]
        endItemID = editorEdge['endItemId']
        key = (start, end, startItemID, endItemID)
        assert key not in edgeSet
        edgeSet.add(key)


class TypeMismatchError(Exception):
    def __init__(self, message, nodeID, argTypeID):
        super(self.__class__, self).__init__(message)
        self.nodeID = nodeID
        self.argTypeID = argTypeID


class Node(object):
    def __init__(self):
        self.name = None
        self.nodeType = None
        self.nodeID = None
        self.nodeDef = None
        self.args = {}
        self.returns = {}
        self.eventLinks = {}
        self.preLinks = {}
        self.funcs = {}

        self.noEventPreLinks = {}

    def is_node(self, nodeName, nodeType):
        if self.name == nodeName or self.nodeType == nodeType:
            assert self.name == nodeName
            assert self.nodeType == nodeType
            return True
        return False


def validate_type(value, argType):
    if argType == 'Int':
        return type(value) == int
    elif argType == 'Float':
        return type(value) == float
    elif argType == 'Bool':
        return type(value) == bool
    elif argType == 'String':
        return type(value) == str
    elif argType == 'List':
        return type(value) == list
    elif argType == 'Dict':
        return type(value) == dict
    elif argType == 'Tuple':
        return type(value) == tuple
    elif argType == 'Set':
        return type(value) == set
    elif argType == 'Any':
        return True
    return False


def generate_node_graph(defData, editorData):
    # 格式 name_id: {node}
    defData = {node['name'][1]: node for node in defData}
    nodes = {}
    defaultNoneValue = Value()
    for editorNode in editorData["nodes"]:
        node = Node()
        nodes[editorNode['id']] = node
        node.nodeType = editorNode['type']  # name_id
        node.nodeID = editorNode['id']  # 导出节点唯一id
        nodeDef = defData[node.nodeType]  # {} 一个节点数据
        node.name = nodeDef['name'][0]  # Start
        node.nodeDef = nodeDef  # 一个节点数据

        for returnDef in nodeDef['returns']:
            returnType = returnDef['type']
            returnName = returnDef['name'][0]
            returnUUID = returnDef['name'][1]
            if returnType == 'Event':
                node.eventLinks[returnUUID] = {
                    'name': returnName,
                    'links': []
                }
            else:
                valueRef = Value()  # 数据引用
                if 'value' in returnDef:
                    valueRef.value = returnDef['value']
                    assert validate_type(valueRef.value, returnType)
                node.returns[returnUUID] = {
                    'name': returnName,
                    'type': returnType,
                    'valueRef': valueRef,
                    'linked': False
                }

        for (order, argDef) in enumerate(nodeDef["args"]):
            argType = argDef['type']
            argName = argDef["name"][0]
            argUUID = argDef["name"][1]
            argOrder = order

            if argType == 'Event':
                node.funcs[argUUID] = argDef.get('action', None) or argDef.get('function')
                node.preLinks[argUUID] = {
                    'name': argName,
                    'links': []
                }
            else:
                node.args[argUUID] = {
                    'name': argName,
                    'type': argType,
                    'valueRef': defaultNoneValue,
                    'order': argOrder,
                    'argDef': argDef,
                    'dataProvider': None,
                }

                if argUUID in editorNode['args']:
                    value = Value()
                    if editorNode['args'][argUUID] is None:
                        value = defaultNoneValue  # Value()
                    else:
                        value.value = editorNode['args'][argUUID]
                    try:
                        assert validate_type(value.value, argType)
                    except:
                        raise TypeMismatchError(
                            'validate_type error, argName "%s", type of (%s) is not %s, %s, def is %s' % (
                                argName, value.value, argType, type(value.value), node.nodeDef), node.nodeID,
                            argUUID)
                    node.args[argUUID]['valueRef'] = value
                    node.args[argUUID]['dataProvider'] = node

        # 添加节点索引id, 作为参数
        node_idx = Value()
        node_idx.value = node.nodeID
        node.args.update({node.nodeID: {'name': 'node_index', 'valueRef': node_idx}})

    for editorEdge in editorData["edges"]:
        startNode = nodes[editorEdge["start"]]
        endNode = nodes[editorEdge["end"]]

        if editorEdge['linktype'] == 'Event':
            assert editorEdge['endItemId'] in endNode.funcs

            startNode.eventLinks[editorEdge["startItemId"]]['links'].append({
                'node': endNode,
                'eventUUID': editorEdge['endItemId'],
                'funcID': endNode.funcs[editorEdge['endItemId']]
            })
            endNode.preLinks[editorEdge['endItemId']]['links'].append({
                'node': startNode,
                'eventUUID': editorEdge['startItemId']}
            )
        else:
            # NOTE: 如果一个节点已经手工写了值了，那么不应该再由其他节点提供值
            try:
                assert endNode.args[editorEdge["endItemId"]]['valueRef'] is defaultNoneValue
            except:
                print("endNode '%s', attribute '%s', value is '%s', which should be None" % (
                    endNode.name, endNode.args[editorEdge["endItemId"]]['name'],
                    endNode.args[editorEdge["endItemId"]]['valueRef'].value))
                raise

            assert endNode.args[editorEdge["endItemId"]]['dataProvider'] is None

            endNode.args[editorEdge["endItemId"]]['valueRef'] = startNode.returns[editorEdge["startItemId"]]['valueRef']
            startNode.returns[editorEdge["startItemId"]]["linked"] = True
            endNode.args[editorEdge["endItemId"]]['dataProvider'] = startNode

            # NOTE: 允许Any类型节点接受任何输入，允许任何类型接受Any类型的输入，其他情况下保持两侧类型一致
            assert endNode.args[editorEdge["endItemId"]]['type'] == startNode.returns[editorEdge["startItemId"]][
                'type'] or endNode.args[editorEdge["endItemId"]]['type'] == 'Any' or \
                   startNode.returns[editorEdge["startItemId"]]['type'] == 'Any'
    return nodes


def do_work(defData, editorData, filename):
    nodeGraph = generate_node_graph(defData, editorData)
    nodes = []
    roots = []

    idx = 0
    for node in nodeGraph.values():
        node.idx = idx
        # node.nodeID
        nodes.append(None)
        idx += 1

    runTimeData = []

    for node in nodeGraph.values():
        if node.name == 'Start':
            roots.append(node.idx)
            break

    for node in nodeGraph.values():
        for retUUID, value in node.returns.items():
            valueRef = value['valueRef']

            if valueRef.idx is None:
                idx = len(runTimeData)

                valueRef.idx = idx
                runTimeData.append(valueRef.value)

    for node in nodeGraph.values():
        for argUUID, value in node.args.items():
            valueRef = value['valueRef']

            if valueRef.idx is None:
                idx = len(runTimeData)
                valueRef.idx = idx
                runTimeData.append(valueRef.value)

    for node in nodeGraph.values():
        args = {value['name']: value['valueRef'].idx for argUUID, value in node.args.items()}

        pre_nodes = set(value['dataProvider'] for value in node.args.values() if
                        value.get('dataProvider') and value.get('dataProvider').idx != node.idx)
        no_event_pre_nodes = [nd for nd in pre_nodes if not nd.preLinks]
        no_event_prelinks = {nd.idx: 'Null' for nd in no_event_pre_nodes}

        returns = {value['name']: value['valueRef'].idx for _, value in node.returns.items()}

        eventLinks = {value['name']: {link['node'].idx: 'In' for link in value['links']} for
                      eventUUID, value in node.eventLinks.items()}
        # eventLinks = {value['name']: [(link['node'].idx, link['funcID']) for link in value['links']] for
        #               eventUUID, value in node.eventLinks.items()}

        prelinks = {}
        for value in node.preLinks.values():
            if value['links']:
                prelinks[value['name']] = [node.funcs[key] for key in node.funcs][0]
            else:
                prelinks['Default'] = 'Start'

        if not node.preLinks:
            prelinks['Null'] = node.name

        nodes[node.idx] = {
            # 'preQueryNodes': preQueryNodes,
            'event_actions': prelinks,
            'event_links': eventLinks,
            'inputs': args,
            'outputs': returns,
            'no_event_prelinks': no_event_prelinks
        }

    ret = {
        'nodes': nodes,
        'runtime_data': runTimeData,
        'roots': roots
    }
    return ret


def single_file_export(editorData):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    nodeDefFilepath = '/'.join([current_dir, 'meta/nodes.json'])

    filename = os.path.basename(nodeDefFilepath).split('.')[0]
    # defData = json.loads(open(nodeDefFilepath, 'r').read())
    defData = loadJsonData('meta/nodes.json')

    validate_def_data(defData)
    validate_editor_data(editorData)

    result = do_work(defData, editorData, filename)
    return result


def convertFile(editorFilepath):
    import traceback, sys
    editorData = json.loads(open(editorFilepath, 'r').read())

    try:
        result = single_file_export(editorData)
        # pprint(result)
    except Exception as e:
        traceback.print_exc(file=sys.stderr)
        return False

    parts = os.path.splitext(editorFilepath)
    newFilename = parts[0] + '.txt'
    with open(newFilename, 'w') as f:
        # json.dump(result, f, indent=4)
        f.write(str(result))
        # f.write(json.dumps(result, ensure_ascii=False, indent=2))
    return True


if __name__ == '__main__':
    editorFilepath = 'E:\\crawler\\crawler_graph\\editor\\graph\\noin.json'
    convertFile(editorFilepath)
