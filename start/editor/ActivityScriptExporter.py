# coding: utf-8
import os

import math
import csv
import re
import traceback

"""
	NOTE: 预存数据的runTimeData仅支持以下几种类型

	1. String -> string
	2. Float -> float
	3. Int -> int
	4. None -> None
	5. Vec3 -> (a, b, c) -> math3d.vector

	这里使用tuple表示Vec3, 故tuple数据类型被占用
"""

# TODO: 数据校验
# TODO: const function 内敛
# TODO: Vec3

CLIENT_SCRIPT = "client"
SERVER_SCRIPT = "server"


class NoneValueError(Exception):
    def __init__(self, message, nodeID, argTypeID):
        super(NoneValueError, self).__init__(message)

        self.nodeID = nodeID
        self.argTypeID = argTypeID


class TypeMismatchError(Exception):
    def __init__(self, message, nodeID, argTypeID):
        super(TypeMismatchError, self).__init__(message)

        self.nodeID = nodeID
        self.argTypeID = argTypeID


class Node(object):
    def __init__(self):
        self.name = None

        self.nodeType = None

        # self.preQueryNodes = []
        self.args = {}
        self.returns = {}
        self.eventLinks = {}
        self.preLinks = {}

        self.funcs = {}

        self.nodeDef = None

    def is_node(self, nodeName, nodeType):
        if self.name == nodeName and self.nodeType == nodeType:
            assert self.name == nodeName
            assert self.nodeType == nodeType
            return True

        return False


class Value(object):
    def __init__(self):
        self.idx = None
        self.value = None


def num_events_in_args(nodeDef):
    count = 0

    for arg in nodeDef['args']:
        if arg['type'] == 'Event':
            count += 1

    return count


def string_to_vec3(value):
    assert value[:5] == "Vec3("
    assert value[-1] == ")"

    a, b, c = value[5:-1].split(',')

    a = float(a)
    b = float(b)
    c = float(c)

    return (a, b, c)


def extract_multiple_string(value):
    # Note: csv.reader需要一个迭代器作为参数，所以这里包装一下
    # TODO: 这里转出来不是unicode?

    data = next(csv.reader([value], quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True))

    return data


def validate_type(value, argType):
    if argType == 'Int':
        return type(value) == int
    elif argType == 'Float':
        return type(value) == float
    elif argType == 'Bool':
        return type(value) == bool
    elif argType == 'String':
        return type(value) == str
    elif argType == 'Vec3':
        return type(value) == tuple and len(value) == 3 and type(value[0]) == float and type(
            value[1]) == float and type(value[2]) == float

    return True


def validate_def_data(defData):
    from uuid import UUID

    uuidSet = set()

    for nodeDef in defData:
        for arg in nodeDef['args']:
            uuid = arg['name'][1]

            try:
                assert uuid not in uuidSet
            except:
                print('Duplicate UUID !!! : ', uuid)
                raise

            assert UUID(uuid, version=4)

            uuidSet.add(uuid)

            if 'default' in arg:
                try:
                    value = arg['default']

                    if arg['type'] == 'Vec3':
                        value = string_to_vec3(value)

                    assert validate_type(value, arg['type'])
                except:
                    print('Wrong default value type: ', arg)
                    raise

        for ret in nodeDef['returns']:
            uuid = ret['name'][1]

            try:
                assert uuid not in uuidSet
            except:
                print('Duplicate UUID !!! : ', uuid)
                raise

            # assert UUID(uuid, version=4)

            uuidSet.add(uuid)

        uuid = nodeDef['name'][1]

        try:
            assert uuid not in uuidSet
        except:
            print('Duplicate UUID !!! : ', uuid)
            raise

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
                print('Def Error, event does not have func', nodeDef)
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


def generate_node_graph(defData, editorData):
    defData = {node['name'][1]: node for node in defData}

    nodes = {}

    defaultNoneValue = Value()

    for editorNode in editorData["nodes"]:
        node = Node()
        nodes[editorNode['id']] = node

        node.nodeType = editorNode['type']
        node.nodeID = editorNode['id']

        nodeDef = defData[node.nodeType]  # {} 一个节点

        node.name = nodeDef['name'][0]
        node.nodeDef = nodeDef

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
                valueRef = Value()

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
                # TODO
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

                    if argType == 'Vec3':
                        try:
                            value.value = string_to_vec3(editorNode['args'][argUUID])
                        except:
                            raise TypeMismatchError(
                                'validate_type Vec3 error, argName "%s", type of (%s) is not %s, def is %s' % (
                                    argName, value.value, argType, node.nodeDef), node.nodeID, argUUID)
                    else:
                        if editorNode['args'][argUUID] is None:
                            value = defaultNoneValue
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

            if startNode.nodeDef.get('query', False):
                endNode.preQueryNodes.append(startNode)

            endNode.args[editorEdge["endItemId"]]['valueRef'] = startNode.returns[editorEdge["startItemId"]]['valueRef']
            startNode.returns[editorEdge["startItemId"]]["linked"] = True
            endNode.args[editorEdge["endItemId"]]['dataProvider'] = startNode

            # NOTE: 允许Any类型节点接受任何输入，允许任何类型接受Any类型的输入，其他情况下保持两侧类型一致
            assert endNode.args[editorEdge["endItemId"]]['type'] == startNode.returns[editorEdge["startItemId"]][
                'type'] or endNode.args[editorEdge["endItemId"]]['type'] == 'Any' or \
                   startNode.returns[editorEdge["startItemId"]]['type'] == 'Any'

    for node in nodes.values():
        for argUUID, arg in node.args.items():
            argDef = arg['argDef']
            argType = argDef['type']

            if argType == 'Event':
                continue
            argValueRef = arg['valueRef']
            argValue = arg['valueRef'].value

            if argValue is None:
                if argDef.get('valueCanBeNone', False):
                    pass
                else:
                    try:
                        assert arg['dataProvider'] is not None
                        assert arg['dataProvider'] is not node
                    except:
                        raise NoneValueError('value error, argName "%s" of node [ %s ] can not be None' % (
                            argDef['name'][0], node.nodeDef['name'][0]), node.nodeID, argUUID)
            else:

                try:
                    assert validate_type(argValue, argType)
                except:
                    raise TypeMismatchError(
                        'validate_type error, argName "%s", type of (%s) is not %s, %s, def is %s' % (
                            argDef['name'][0], argValue, argType, type(argValue), node.nodeDef), node.nodeID,
                        argUUID)

            if argDef.get('ensureStaticConst') and argValueRef is not defaultNoneValue:
                try:
                    assert arg['dataProvider'] is node
                except:
                    raise TypeMismatchError(
                        'validate_type error, value must be static const, argName "%s", type of (%s) is not %s, def is %s' % (
                            argDef['name'][0], argValue, argType, node.nodeDef), node.nodeID, argUUID)

    return nodes


def do_work(defData, editorData, byEditor, filename, is_city=None):
    nodeGraph = generate_node_graph(defData, editorData)

    # NOTE: 这里做了一些trick，来把string转换成list，避免运行时转换开销
    for node in nodeGraph.values():
        if node.is_node('Random Select String', 'a6bfe777-df7c-484c-b16d-71259527dca4'):
            assert node.nodeDef['function']
            assert node.nodeDef['query'] is True

            assert num_events_in_args(node.nodeDef) is 0

            assert len(node.preQueryNodes) is 0
            assert len(node.args) is 1

            arg = next(iter(node.args.values()))

            assert arg['dataProvider'] is node

            value = extract_multiple_string(arg['valueRef'].value)

            assert len(value) > 0

            for v in value:
                if len(v) <= 0 or not isinstance(v, str):
                    print("Wrong value format in random_select_string", node)
                    raise EOFError

            arg['valueRef'].value = value

        elif node.is_node('Play SFX', '79e89d07-876e-4b9e-a00d-c3f1221582b6'):
            degreeArg = node.args['34c3310e-4df4-403f-adda-d5786a4345f5']
            degreeArgValue = degreeArg['valueRef'].value

            if degreeArgValue is not None:
                arcArg = node.args['e5785ef1-3c37-402b-883d-20116aaa63c7']
                arcArg['valueRef'].value = degreeArgValue / 180.0 * math.pi

        elif node.is_node('Set Int Variable', "bf7eab3f-b0b2-426f-9ddc-355c930ec0e6"):
            assert len(node.args) is 2

            arg = node.args['d4444300-2f7a-4ea2-80a0-40ed7b393d78']

            if arg['dataProvider'] is node:
                assert type(arg['valueRef'].value) is int

        elif node.is_node('Set Variable', '7532929c-3d5e-4264-92cc-7f0b5c7ca0b7'):
            assert len(node.args) is 2

            arg = node.args['17ddb382-4d7f-47b4-a1f1-929bd74cf91e']
            assert arg['dataProvider'] is not node, "use 'Set XXX Variable' instead"

        elif node.is_node('Array Data(Int)', 'bf11a6e1-e92d-4cb9-80dd-0e3cd22f164a'):
            assert node.nodeDef['function']
            assert node.nodeDef['query'] is True

            assert num_events_in_args(node.nodeDef) is 0

            assert len(node.preQueryNodes) is 0
            assert len(node.args) is 1

            arg = next(iter(node.args.values()))

            assert arg['dataProvider'] is node

            value = list(map(int, arg['valueRef'].value.split(',')))
            assert len(value) > 0

            arg['valueRef'].value = value

        elif node.is_node('Array Data(Float)', '800cdc88-c30e-4b7f-8d39-d3f3843e53df'):
            assert node.nodeDef['function']
            assert node.nodeDef['query'] is True

            assert num_events_in_args(node.nodeDef) is 0

            assert len(node.preQueryNodes) is 0
            assert len(node.args) is 1

            arg = next(iter(node.args.values()))

            assert arg['dataProvider'] is node

            value = list(map(float, arg['valueRef'].value.split(',')))
            assert len(value) > 0

            arg['valueRef'].value = value

        elif node.is_node('Array Data(String)', '400d6243-58e4-43e1-a1fc-34fa41a421ff'):
            assert node.nodeDef['function']
            assert node.nodeDef['query'] is True

            assert num_events_in_args(node.nodeDef) is 0

            assert len(node.preQueryNodes) is 0
            assert len(node.args) is 1

            arg = next(iter(node.args.values()))

            assert arg['dataProvider'] is node

            value = extract_multiple_string(arg['valueRef'].value)
            assert len(value) > 0

            for v in value:
                if len(v) <= 0 or not isinstance(v, str):
                    print("Wrong value format in random_select_string", node)
                    raise Exception

            arg['valueRef'].value = value

        elif node.is_node('Random Select Float', 'ca345a9f-56d9-4197-b6e3-1dfc65dfae0c'):
            assert node.nodeDef['function']
            assert node.nodeDef['query'] is True

            assert num_events_in_args(node.nodeDef) is 0

            assert len(node.preQueryNodes) is 0
            assert len(node.args) is 1

            arg = next(iter(node.args.values()))

            assert arg['dataProvider'] is node

            value = list(map(float, arg['valueRef'].value.split(',')))
            assert len(value) > 0

            arg['valueRef'].value = value

        elif node.is_node('Random Select Integer', '4e0fa583-7ba8-40d1-82d2-375d98b95500'):
            assert node.nodeDef['function']
            assert node.nodeDef['query'] is True

            assert num_events_in_args(node.nodeDef) is 0

            assert len(node.preQueryNodes) is 0
            assert len(node.args) is 1

            arg = next(iter(node.args.values()))
            assert arg['dataProvider'] is node

            value = list(map(int, arg['valueRef'].value.split(',')))
            assert len(value) > 0

            arg['valueRef'].value = value

        elif node.is_node('Open NPC Dialog', 'e0e5d422-f970-429b-8a62-7b5fcae3a5c4'):
            arg = node.args.get('d10b29b5-7276-4df1-84ca-7fec5fc44b67', None)
            value = arg['valueRef'].value
            if value:
                talk_list = []
                for item in value.split(';'):
                    talk_item = item.split(',')
                    assert len(talk_item) == 2
                    talk_item[1] = int(talk_item[1])
                    talk_item[0] = str(talk_item[0])
                    talk_list.append(talk_item)
                arg['valueRef'].value = talk_list

        elif node.is_node('Open NPC Dialog(Only In Dungeon)', '32cff2f0-7157-4d59-a658-13fdbae44b6d'):
            arg = node.args.get('361036ea-5700-4e79-bed8-1c0a84c64f16', None)
            value = arg['valueRef'].value
            if value:
                talk_list = []
                for item in value.split(';'):
                    talk_item = item.split(',')
                    assert len(talk_item) == 2
                    talk_item[1] = int(talk_item[1])
                    talk_item[0] = str(talk_item[0])
                    talk_list.append(talk_item)
                arg['valueRef'].value = talk_list

        elif node.is_node('Play Cinematic', '8d21cbcb-287f-48f9-8aa9-71b9293a6348'):
            def get_num(reg_str, prefix_len, line):
                index = re.search(reg_str, line)
                if index:
                    length = index.group(0)
                    length = length[prefix_len:-1]
                    return float(length)
                return 0

            path_arg = node.args.get('954cde6d-c8cc-4b61-bc48-19e0a0d60987', None)
            path = path_arg['valueRef'].value
            if path:
                anim_file = os.path.join(resPath, path)
                if os.path.exists(anim_file):
                    try:
                        anim_file_handle = open(anim_file, 'r')
                        lines = anim_file_handle.readlines()
                        length = get_num('''length = "[0-9.]*''', len('length = "'), lines[0])
                        if length:
                            start_black_time = get_num('''start_black_time = "[0-9.]*''', len('start_black_time = "'),
                                                       lines[0])
                            length += start_black_time
                            end_black_time = get_num('''end_black_time = "[0-9.]*''', len('end_black_time = "'),
                                                     lines[0])
                            length += end_black_time
                            path_arg['valueRef'].value = path + ';' + str(length)
                        else:
                            print('Error: can not find length in ', anim_file)
                            traceback
                    except Exception as e:
                        print('Error: get anim length failed, ', anim_file, e)
                        traceback
                else:
                    print('Error: open anim_file failed, ', anim_file)
                    traceback
            player_id_arg = node.args.get('4407dd3a-9af0-46f3-a82d-ca47f5ed9b8a', None)
            if not player_id_arg.get('dataProvider') and is_city is True:
                raise Exception('Play Cinematic, but Player EntityID == None is forbid in city level!!')

        elif node.is_node('Start Unit Dialog Tips', '5c7c06b0-b06c-49b7-afaf-e2473cb12c10'):
            player_id_arg = node.args.get('9eef619e-0ffc-488a-89dd-276ba67dcdb5', None)
            player_id = player_id_arg['valueRef'].value
            if not player_id and is_city is True:
                raise Exception('Start Unit Dialog Tips, but Player EntityID == None is forbid in city level!!')

        elif node.is_node('Advance Task', '217dd054-8c6e-4976-bf3c-9defbc218c74'):
            for_all_players_arg = node.args.get('9ddf1c84-db67-421e-951c-4607821abdd8', None)
            for_all_players = for_all_players_arg['valueRef'].value
            if for_all_players and is_city is True:
                raise Exception('Advance Task, but \'For All Players\' == True is forbid in city level!!')

        elif node.is_node('Create Mechanism', 'f0f220b5-e584-4aff-8c86-f039d030c02b'):
            arg = node.args.get('b6e0a54f-b5b2-11e5-8bb7-448a5b598860', None)
            value = arg['valueRef'].value
            if value:
                value = value.split(',')
                arg['valueRef'].value = value
        elif node.is_node('Create Mechanism With Lightmap', '03cfda15-a336-4c6c-b8a4-75123e88628d'):
            arg = node.args.get('cf1d99e2-a1b7-48e8-ad79-40014ef128bf', None)
            value = arg['valueRef'].value
            if value:
                value = value.split(',')
                arg['valueRef'].value = value

            # NOTE: lightmap 信息导出
            arg = node.args['6fd92e9d-7e74-414a-a662-c411aee4f19d']
            value = arg['valueRef'].value
            value = extract_multiple_string(value)

            assert len(value) == 2
            arg['valueRef'].value = value

        elif node.is_node('Set Enable Player Skills', '49c402b3-022a-47e8-8028-1401c78b332c'):
            arg = node.args.get('ea57e264-6569-4dba-8b0a-0995f1f0825c')  # Skill ID List
            value = list(map(int, arg['valueRef'].value.split(',')))
            assert len(value) > 0
            arg['valueRef'].value = value

    nodes = []

    idx = 0
    for node in nodeGraph.values():
        node.idx = idx
        nodes.append(None)
        idx += 1

    runTimeData = []

    # 先完成所有节点的转换后再进行遍历
    trigger_grids_all = {}

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
        # if len(node.preQueryNodes) > 0:
        #     preQueryNodes = [(preQueryNode.idx, preQueryNode.nodeDef['function']) for preQueryNode in
        #                      node.preQueryNodes]
        # else:
        #     preQueryNodes = None

        """
        # TODO: 缓存优化
        args = [ (value['order'], value['valueRef'].idx) for argUUID, value in node.args.iteritems() ]
        args.sort(key = lambda x : x[0])
        args = tuple([ value[1] for value in args ])
        """

        # TODO: Vector
        args = {value['name']: value['valueRef'].idx for argUUID, value in node.args.items()}
        returns = {value['name']: value['valueRef'].idx for _, value in node.returns.items()}
        # returns_linked = False
        # for retUUID, value in node.returns.items():
        #     returns.append((value['name'], value['valueRef'].idx))
        #     # returns_linked |= value['linked']
        # returns = tuple(returns)

        # eventLinks = {value['name']: {link['node'].idx: 'In' for link in value['links']} for
        #               eventUUID, value in node.eventLinks.items()}
        eventLinks = {value['name']: [(link['node'].idx, link['funcID']) for link in value['links']] for
                      eventUUID, value in node.eventLinks.items()}

        prelinks = {}
        for value in node.preLinks.values():
            # if value['links']:
            prelinks[value['name']] = [node.funcs[key] for key in node.funcs][0]

        if byEditor:
            nodes[node.idx] = {
                # 'preQueryNodes': preQueryNodes,
                'eventLinks': eventLinks,
                'args': args,
                'returns': returns,
                'preLinks': prelinks,
                'nodeUUidIdx': (node.nodeID, node.idx)
            }
        else:
            nodes[node.idx] = {
                # 'preQueryNodes': preQueryNodes,
                'event_actions': prelinks,
                'event_links': eventLinks,
                'inputs': args,
                'outputs': returns,
            }

            # if returns_linked:
            #     nodes[node.idx]['returns_linked'] = True

    """
        针对外部事件的特殊处理
    """

    def append_runtime_data(value):
        runTimeData.append(value)
        return len(runTimeData) - 1

    on_script_start = []
    on_player_load_scene_finish = []
    on_player_unit_dead = []

    levelEventListeners = {
        'on_script_start': on_script_start,
        'on_player_load_scene_finish': on_player_load_scene_finish,
        'on_player_unit_dead': on_player_unit_dead
    }
    clientEventListeners = {}
    taskEventListeners = {}
    activityStartListeners = {}
    levelTimesUseoutEventListeners = {}
    openPublicInstnaceEventListeners = {}
    # staticMechanisms = []
    questionEventListeners = []

    STATIC_MECHANISM_PARAMS = {
        'Mechanism Config ID': 'mechanism_config_id',
        'Block Point': 'block_point',
        'Spawn Point': 'spawn_point',
        'Tile Index': 'tile_index',
        'Unit Type': 'unit_type'
    }

    autoCreatePlayerUnitNodeCount = 0
    setColorThemeNodeCount = 0

    BUILTIN_LEVEL_EVENTS = ['on_script_start', 'on_player_load_scene_finish', 'on_player_unit_dead']

    AddTaskDetailRequiredNames = {}
    CounterNames = {}

    mechanism_with_blcok = set()
    has_opt_mechanism = set()
    for node in nodeGraph.values():
        if node.name == 'On Script Start' or node.nodeType == 'f8af0dbe-14b1-415d-bc91-5eb68bd2bd06':
            assert node.nodeType == 'f8af0dbe-14b1-415d-bc91-5eb68bd2bd06'
            assert node.name == 'On Script Start'
            assert node.nodeDef['function']

            assert num_events_in_args(node.nodeDef) is 0

            on_script_start.append((node.idx, node.nodeDef['function']))

        elif node.is_node("Create NPC", "83e7076d-9d00-4415-9e9f-d121c6d0d2e6"):
            if node.args['2c5d3d12-509f-45ce-ba8d-b8590c12739c']['dataProvider'] is None:  # Position
                arg = node.args['7032826b-37c5-4299-a172-2621c92ef289']  # Spawn Point
                argValue = arg['valueRef'].value

                if argValue is None:
                    assert arg['dataProvider'] is not node
                    assert arg['dataProvider'] is not None

        elif node.is_node("Create Monster", "b8bdb1c4-48e3-4c7b-b38e-12aef4a29db0"):
            if node.args['ad60708a-4917-4fef-a193-9e1d62d2e8bd']['dataProvider'] is None:  # Position
                arg = node.args['33228f1d-1b7a-405d-82d4-7958acc8e8dc']  # Spawn Point
                argValue = arg['valueRef'].value

                if argValue is None:
                    assert arg['dataProvider'] is not node
                    assert arg['dataProvider'] is not None

        elif node.is_node("Create Monster Boss", "f7454550-56f5-4242-86a8-9e46b140feab"):
            if node.args['8b062406-a831-4a43-baad-9c7bd65a84ef']['dataProvider'] is None:  # Position
                arg = node.args['40c74e07-8e28-4366-bd92-25e5d3c97dc7']  # Spawn Point
                argValue = arg['valueRef'].value

                if argValue is None:
                    assert arg['dataProvider'] is not node
                    assert arg['dataProvider'] is not None

        elif node.is_node("Create Monster Avatar", "9d1d78e6-0591-4b88-b34f-2a6864252151"):
            if node.args['8dc0f1c1-188d-4e41-979f-737bda223697']['dataProvider'] is None:  # Position
                arg = node.args['2c74e5fd-8695-4bd2-aa71-9a28ff8ad5a6']  # Spawn Point
                argValue = arg['valueRef'].value

                if argValue is None:
                    assert arg['dataProvider'] is not node
                    assert arg['dataProvider'] is not None

        elif node.is_node("Create Monster World Boss", "f7454550-56f5-4242-86a8-9e46b141feab"):
            if node.args['40c74e07-8e28-4366-bd92-25e5d3c97dc8']['dataProvider'] is None:  # Position
                arg = node.args['8b062406-a831-4a43-baad-9c7bd65a85ef']  # Spawn Point
                argValue = arg['valueRef'].value

                if argValue is None:
                    assert arg['dataProvider'] is not node
                    assert arg['dataProvider'] is not None

        elif node.is_node("Create Mechanism", "f0f220b5-e584-4aff-8c86-f039d030c02b"):
            if node.args['cb7c120d-aa4d-4adc-8a09-20ecd5b539c0']['dataProvider'] is None:  # Position
                arg = node.args['b84f6f5c-695f-4b56-b98b-3bd61698bd3c']  # Spawn Point
                argValue = arg['valueRef'].value

                if argValue is None:
                    assert arg['dataProvider'] is not node
                    assert arg['dataProvider'] is not None


        elif node.name == 'On Level Loaded' or node.nodeType == 'e468c7df-0563-4f68-9c8f-daf2e77d08b7':
            assert node.name == 'On Level Loaded'
            assert node.nodeType == 'e468c7df-0563-4f68-9c8f-daf2e77d08b7'
            assert node.nodeDef['function']

            assert num_events_in_args(node.nodeDef) is 0

            on_player_load_scene_finish.append((node.idx, node.nodeDef['function']))

        elif node.is_node('Auto Create Player Unit', '02b886bc-365f-4913-bae0-3dbf270633f3'):
            assert autoCreatePlayerUnitNodeCount == 0

            assert node.nodeDef['function']

            assert num_events_in_args(node.nodeDef) is 0

            autoCreatePlayerUnitNodeCount += 1

            on_player_load_scene_finish.append((node.idx, node.nodeDef['function']))

        elif node.is_node('Add Task Detail', '3d934991-fcfe-44f4-8129-35295f0e4393'):
            arg = node.args['8519ec91-87de-48a3-a049-47c107f7ac39']
            assert arg['name'] == 'Counter Name'
            name = arg['valueRef'].value
            assert not name in AddTaskDetailRequiredNames
            AddTaskDetailRequiredNames[name] = node
        elif node.is_node('Counter', '7035072e-0ca7-4ec4-b36b-0a25123386fe'):
            arg = node.args['fbed0f80-12ad-48a2-a3a3-e733ee0b6c01']
            assert arg['name'] == 'Name'
            name = arg['valueRef'].value

            if name is not None:
                assert not name in CounterNames
                CounterNames[name] = node
        elif node.is_node('Create Static Object', '9ed37096-bc78-47c9-b0d0-44fef1f8002d'):

            # NOTE: 创建静态机关，先放在这里，之后再调整
            on_script_start.append((node.idx, 'create_static_object'))

        elif node.is_node('On Player Unit Dead', '95d00220-6cc5-4ecd-bbe7-73bbfbd827a7'):
            assert num_events_in_args(node.nodeDef) is 0

            on_player_unit_dead.append((node.idx, node.nodeDef['function']))

        elif node.name == 'On Level Event' or node.nodeType == '7c2ac230-a0dd-41a7-a3f3-c501cfce7e59':
            assert node.name == 'On Level Event'
            assert node.nodeType == '7c2ac230-a0dd-41a7-a3f3-c501cfce7e59'

            assert len(node.args) == 1

            eventName = list(node.args.values())[0]['valueRef'].value

            assert list(node.args.values())[0]['dataProvider'] is node

            assert eventName not in BUILTIN_LEVEL_EVENTS

            if eventName in levelEventListeners:
                levelEventListeners[eventName].append((node.idx, node.nodeDef['function']))
            else:
                levelEventListeners[eventName] = [(node.idx, node.nodeDef['function'])]

        elif node.name == 'Response Server Event' or node.nodeType == '0a8f2f1b-1999-411c-b690-662924beef44':
            assert node.name == 'Response Server Event'
            assert node.nodeType == '0a8f2f1b-1999-411c-b690-662924beef44'
            assert len(node.args) == 1

            eventName = list(node.args.values())[0]['valueRef'].value

            assert list(node.args.values())[0]['dataProvider'] is node

            if eventName in clientEventListeners:
                clientEventListeners[eventName].append((node.idx, node.nodeDef['function']))
            else:
                clientEventListeners[eventName] = [(node.idx, node.nodeDef['function'])]

        elif node.name == 'Trigger Client Event' or node.nodeType == 'e4a4da2b-d039-4c91-9fc6-4287557cee1f':
            assert node.name == 'Trigger Client Event'
            assert node.nodeType == 'e4a4da2b-d039-4c91-9fc6-4287557cee1f'

            assert len(node.args) == 3

        elif node.name == 'On UI Event' or node.nodeType == '2415af72-a28a-4647-a484-51b94f75c89e':
            assert node.name == 'On UI Event'
            assert node.nodeType == '2415af72-a28a-4647-a484-51b94f75c89e'
            assert len(node.args) == 1

            eventName = list(node.args.values())[0]['valueRef'].value
            assert list(node.args.values())[0]['dataProvider'] is node

            assert eventName not in BUILTIN_LEVEL_EVENTS

            if eventName in levelEventListeners:
                levelEventListeners[eventName].append((node.idx, node.nodeDef['function']))
            else:
                levelEventListeners[eventName] = [(node.idx, node.nodeDef['function'])]

        elif node.name == 'On Task Event' or node.nodeType == '0dafa7b6-28f5-424a-83b3-bc6cc7728016':
            assert node.name == 'On Task Event'
            assert node.nodeType == '0dafa7b6-28f5-424a-83b3-bc6cc7728016'

            assert len(node.args) == 1

            eventName = list(node.args.values())[0]['valueRef'].value
            assert list(node.args.values())[0]['dataProvider'] is node

            assert eventName not in BUILTIN_LEVEL_EVENTS  # 从使用上还是有必要

            if eventName in taskEventListeners:
                taskEventListeners[eventName].append((node.idx, node.nodeDef['function']))
            else:
                taskEventListeners[eventName] = [(node.idx, node.nodeDef['function'])]

        elif node.name == 'On Level Times Useout' or node.nodeType == '1a33c290-d57a-47ab-8551-7702e0c96f8e':
            assert node.name == 'On Level Times Useout'
            assert node.nodeType == '1a33c290-d57a-47ab-8551-7702e0c96f8e'

            assert len(node.args) == 1

            levelId = list(node.args.values())[0]['valueRef'].value
            assert list(node.args.values())[0]['dataProvider'] is node

            assert levelId not in BUILTIN_LEVEL_EVENTS

            if levelId in levelTimesUseoutEventListeners:
                levelTimesUseoutEventListeners[levelId].append((node.idx, node.nodeDef['function']))
            else:
                levelTimesUseoutEventListeners[levelId] = [(node.idx, node.nodeDef['function'])]

        elif node.name == 'On Open Public Instance' or node.nodeType == 'ea5801b5-68cb-4a85-bb68-36076c00f1ac':
            assert node.name == 'On Open Public Instance'
            assert node.nodeType == 'ea5801b5-68cb-4a85-bb68-36076c00f1ac'

            assert len(node.args) == 1

            levelId = list(node.args.values())[0]['valueRef'].value
            assert list(node.args.values())[0]['dataProvider'] is node

            assert levelId not in BUILTIN_LEVEL_EVENTS

            if levelId in openPublicInstnaceEventListeners:
                openPublicInstnaceEventListeners[levelId].append((node.idx, node.nodeDef['function']))
            else:
                openPublicInstnaceEventListeners[levelId] = [(node.idx, node.nodeDef['function'])]

        elif node.name == 'On Activity Start' or node.nodeType == 'b7ae0919-bf04-464d-bd9c-5535a8203500':
            assert node.name == 'On Activity Start'
            assert node.nodeType == 'b7ae0919-bf04-464d-bd9c-5535a8203500'

            assert len(node.args) == 1

            activityid = list(node.args.values())[0]['valueRef'].value
            assert list(node.args.values())[0]['dataProvider'] is node

            assert activityid not in BUILTIN_LEVEL_EVENTS

            if activityid not in activityStartListeners:
                activityStartListeners[activityid] = []
            activityStartListeners[activityid].append((node.idx, node.nodeDef['function']))

        elif node.name == 'On Question Event' or node.nodeType == '982dd635-edaf-43d1-a302-a8757cab48f2':
            assert node.name == 'On Question Event'
            assert node.nodeType == '982dd635-edaf-43d1-a302-a8757cab48f2'

            questionEventListeners.append((node.idx, node.nodeDef['function']))

        elif node.name == 'Trigger Level Event' or node.nodeType == '59e9fcdb-1c18-45d9-896d-b85267809adc':
            assert node.name == 'Trigger Level Event'
            assert node.nodeType == '59e9fcdb-1c18-45d9-896d-b85267809adc'

            assert len(node.args) == 1
            assert list(node.args.values())[0]['valueRef'].value not in BUILTIN_LEVEL_EVENTS

        elif node.name == 'Opt Mechanism':
            assert node.name == 'Opt Mechanism'
            if node.args['0d538da7-1471-42c6-ab7b-4035c21ccae3']['valueRef'].value == True:
                mechanismNode = node.args['1411ae69-eaba-4afb-8785-1006a7d2e093']['dataProvider']
                if mechanismNode:
                    idx = mechanismNode.idx
                has_opt_mechanism.add(idx)

        elif node.name == 'Create Mechanism' or node.nodeType == 'f0f220b5-e584-4aff-8c86-f039d030c02b':
            assert node.name == 'Create Mechanism'
            assert node.nodeType == 'f0f220b5-e584-4aff-8c86-f039d030c02b'

            relevantParams = {}
            for value in node.args.values():
                if value['name'] in STATIC_MECHANISM_PARAMS:
                    paramName = STATIC_MECHANISM_PARAMS[value['name']]
                    paramValue = value['valueRef'].value
                    if paramValue is None:
                        if value.get('dataProvider'):
                            strNode = value.get('dataProvider')
                            if strNode.name == 'String Data':
                                paramValue = strNode.args['f1c40cbd-73e8-469c-afde-0375398a510c']['valueRef'].value
                    if paramValue is None:
                        continue
                    relevantParams[paramName] = paramValue

        # if len(relevantParams) == len(STATIC_MECHANISM_PARAMS):

        elif node.name == 'Create Mechanism With Lightmap' or node.nodeType == '03cfda15-a336-4c6c-b8a4-75123e88628d':
            assert node.name == 'Create Mechanism With Lightmap'
            assert node.nodeType == '03cfda15-a336-4c6c-b8a4-75123e88628d'

            relevantParams = {}
            for value in node.args.values():
                if value['name'] in STATIC_MECHANISM_PARAMS:
                    paramName = STATIC_MECHANISM_PARAMS[value['name']]
                    paramValue = value['valueRef'].value
                    if paramValue is None:
                        if value.get('dataProvider'):
                            strNode = value.get('dataProvider')
                            paramValue = strNode.args['f1c40cbd-73e8-469c-afde-0375398a510c']['valueRef'].value
                        else:
                            continue
                    relevantParams[paramName] = paramValue

            if 'mechanism_config_id' in relevantParams and 'unit_type' in relevantParams:
                mechanism_config_id = relevantParams.get('mechanism_config_id')
            if 'mechanism_config_id' in relevantParams:
                mechanism_config_id = relevantParams.get('mechanism_config_id')
        elif node.is_node('Set Color Theme', 'a712c423-d24a-4617-a049-00f4f02b9ebb'):
            assert setColorThemeNodeCount == 0
            assert node.nodeDef['function']
            assert num_events_in_args(node.nodeDef) is 0

            setColorThemeNodeCount += 1

            on_script_start.append((node.idx, node.nodeDef['function']))
            # nodes[node.idx]['args'].append( ('_ColorMultipliers', append_runtime_data([ (1.0, 0.0, 0.0), (0.0, 1.0, 0.0) ])) )

    for idx in mechanism_with_blcok:
        if idx not in has_opt_mechanism:
            for node in nodeGraph.values():
                if idx == node.idx:
                    errorNode = node
                    mechanism_id = errorNode.args
                    for value in errorNode.args.values():
                        if value['name'] == 'Mechanism Config ID':
                            mechanism_id = value['valueRef'].value
                    print('WARNING:mechanism %d is used without open in leve:%s' % (mechanism_id, str(filename)))

    def get_node_arg_index(args, argName):
        for name, argIndex in args:
            if name == argName:
                return argIndex

        raise Exception("cannot find argName %s" % argName)

    for name, node in AddTaskDetailRequiredNames.items():
        assert name in CounterNames

        addTaskDetailNode = nodes[node.idx]
        counterNode = nodes[CounterNames[name].idx]

        if counterNode['preQueryNodes'] is not None:
            if addTaskDetailNode['preQueryNodes'] is None:
                addTaskDetailNode['preQueryNodes'] = []

            addTaskDetailNode['preQueryNodes'].extend(counterNode['preQueryNodes'])

        addTaskDetailNode['args'].append(('_CountNeeded', get_node_arg_index(counterNode['args'], 'Count Needed')))
        addTaskDetailNode['args'].append(('_Value', get_node_arg_index(counterNode['returns'], 'Value')))

        counterNode['eventLinks']['Value Updated'].append((node.idx, 'add_task_detail_counter_updated'))
        counterNode['eventLinks']['Count Reached'].append((node.idx, 'add_task_detail_counter_reached'))

    ret = {
        'nodes': nodes,
        'runTimeData': runTimeData,
    }

    return ret


def single_file_export(defData, editorData, byEditor, filename):
    validate_def_data(defData)
    validate_editor_data(editorData)

    result = do_work(defData, editorData, byEditor, filename)
    # result["staticMechanisms"] = singleStaticMechanisms
    return result


def multi_file_export_mode():
    import sys
    import os

    nodeDefFilepath = sys.argv[1]
    levelScriptsPath = sys.argv[2]
    resPath = sys.argv[3]
    outputPath = os.path.join(sys.argv[4], 'levelscripts')

    # nodeDefFilepath = "F:/H43/design/tools/main/meta/nodes.json"
    # levelScriptsPath = "F:/H43/design/tools/csv2py/levelscripts/"
    # resPath = 'F:/H43/common/neox/res'
    # outputPath = 'F:/ttt'

    defData = json.loads(open(nodeDefFilepath, 'r').read())

    validate_def_data(defData)

    try:
        os.makedirs(outputPath)
    except OSError:
        if not os.path.isdir(outputPath):
            raise

    f = open(os.path.join(outputPath, '__init__.py'), 'wb')
    f.close()

    from output.common.city import data as cityData
    needCheckLevelName = []
    CITY_TYPE_CAMP_BATTLE = 3
    for data in cityData.values():
        if 'use_level_config' in data and data.get('city_type') != CITY_TYPE_CAMP_BATTLE:
            needCheckLevelName.append('level_%d' % data['use_level_config'])

    staticMechanisms = {}
    staticMechanismsFile = 'static_mechanisms.py'

    for filename in os.listdir(levelScriptsPath):
        fullpath = os.path.join(levelScriptsPath, filename)

        if os.path.isfile(fullpath) and fullpath.endswith('.json'):

            outputFilePath = os.path.join(outputPath, os.path.splitext(filename)[0] + '.py')

            print('[ActivityScriptExporter]:', fullpath, '-->', outputFilePath, end=' ')

            editorFilepath = fullpath

            editorData = json.loads(open(editorFilepath, 'r').read())

            validate_editor_data(editorData)

            if os.path.splitext(filename)[0] in needCheckLevelName:
                is_city = True
            else:
                is_city = False

            result, singleStaticMechanisms = do_work(defData, editorData, False, filename.split('.')[0], resPath,
                                                     is_city)
            staticMechanisms[os.path.splitext(filename)[0]] = singleStaticMechanisms

            resultStr = repr(result)

            if is_city:
                if "drop_gift_for_instance" in resultStr:
                    raise Exception('Drop Gift For Instance node in city level!!')
                if "open_npc_dialog_broadcast_mode" in resultStr:
                    raise Exception('open_npc_dialog_broadcast_mode node in city level!!')
            # if "Wait NPC Submit Event Time" in resultStr:
            # raise Exception('use Wait NPC Submit Event Time in city level!!')

            f = open(outputFilePath, 'wb')

            f.write('data = ')
            f.write(resultStr)

            # NOTE: 不能转const，因为vector是用tuple存的，转换会导致脚本层对于类型判定错误
            f.write('\n_reload_all = True\n')

            f.close()

            print(' ... OK')

    outputFilePath = os.path.join(outputPath, staticMechanismsFile)
    print('[ActivityScriptExporter, StaticMechanisms]:', fullpath, '-->', outputFilePath, end=' ')
    f = open(outputFilePath, 'wb')
    f.write('data = ')
    f.write(repr(staticMechanisms))
    f.write('\n_reload_all = True\n')
    f.close()


# NOTE: 编辑器调用，用于验证数据并转换
def editor_validate_and_export(defData, editorData, filename, resPath):
    typeErrors = []
    noneValueErrors = []
    unknownErrors = []

    result = {
        "errors": {
            "TypeErrors": typeErrors,
            "NullValueError": noneValueErrors,
            "UnknownErrors": unknownErrors
        },
        "result": None
    }

    try:
        result['result'] = single_file_export(defData, editorData, True, filename)
    except NoneValueError as e:
        noneValueErrors.append({
            'id': e.nodeID,
            'subItemId': e.argTypeID,
            'message': e.message
        })
    except TypeMismatchError as e:
        typeErrors.append({
            'id': e.nodeID,
            'subItemId': e.argTypeID,
            'message': e.message
        })
    except Exception as e:
        unknownErrors.append(e)

    return result

# if __name__ == '__main__':
#     import sys
#     import os
#     import json
#
#     if len(sys.argv) == 4:
#         nodeDefFilepath = sys.argv[1]
#         editorFilepath = sys.argv[2]
#         resPath = sys.argv[3]
#
#         defData = json.loads(open(nodeDefFilepath, 'r').read())
#         editorData = json.loads(open(editorFilepath, 'r').read())
#
#         result = single_file_export(defData, editorData, False, os.path.basename(nodeDefFilepath).split('.')[0],
#                                     resPath)
#
#         print('data = ', end=' ')
#         print(repr(result))
#
#     elif len(sys.argv) == 5:
#         multi_file_export_mode()
#     else:
#         nodeDefFilepath = 'E:\\PycharmProjects\\crawler\\editor\meta\\nodes.json'
#         editorFilepath = 'E:\\PycharmProjects\\crawler\\editor\\graph\\temp.json'
#         # resPath = 'F:/H43/trunk/Client_Resources/res'
#         defData = json.loads(open(nodeDefFilepath, 'r').read())
#         editorData = json.loads(open(editorFilepath, 'r').read())
#
#         # scriptType = guess_script_type(editorFilepath, editorData)
#
#         result = single_file_export(defData, editorData, False, os.path.basename(nodeDefFilepath).split('.')[0])
#
#         print('data = ', end=' ')
#         print(repr(result))
#         # raise NotImplementedError("wrong args")
#
#     sys.exit(0)
