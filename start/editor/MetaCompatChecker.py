# coding:utf-8
from mutil import loadJsonData, dumpJsonData, setUpLog
import os
import json
import logging
import argparse

debug = False


def hasEditDiff(srcFn, destFn):
    """
    计算srcFn的文件和destFn的文件，是否有编辑上的区别
    计算区别时，会忽略空格和换行符号
    """
    srcMetaData = loadJsonData(srcFn)
    destMetaData = loadJsonData(destFn)

    return srcMetaData != destMetaData


# 检查meta/nodes.json的新版本和老版本之间是否存在着不兼容的问题
class MetaCompatWorker(object):
    CMD_LIST = 'list'
    CMD_UPGRADE = 'upgrade'
    CMD_ATTACH_META = 'attach_meta'
    CMD_LIST_VALUE = 'list_value'
    CMD_VALUE_CHANGE = 'value_change'

    def __init__(self, cmd='list', levelDir=None):
        self.cmd = cmd
        if levelDir is not None:
            self.levelDir = levelDir
        else:
            self.prefs = loadJsonData('meta/prefs.json')
            self.levelDir = self.prefs['open_graph_dir']
        self.nodesDefData = loadJsonData('meta/nodes.json')

    def attachMeta(self):
        """
        给所有的levels添加meta字段，其中只保留该level使用的nodes
        """
        levelFns = os.listdir(self.levelDir)
        for levelFn in levelFns:
            if not levelFn.endswith('.json') or levelFn.endswith('_old.json'):
                continue

            self.attachMetaToFile(levelFn)

    def attachMetaToFile(self, levelFn):
        """
        给levelFn文件添加meta字段
        """
        levelData = loadJsonData(os.path.join(self.levelDir, levelFn))
        if levelData.get('mets', None) is not None:
            return

        print('attach meta to file', levelFn)
        usedNodeKeys = set([node['type'] for node in levelData['nodes']])

        metas = []
        for nodeDef in self.nodesDefData:
            if nodeDef['name'][-1] in usedNodeKeys:
                metas.append(nodeDef)

        levelData['meta'] = metas

        # oldLevelData = loadJsonData(os.path.join(self.levelDir, levelFn))
        # dumpJsonData(os.path.join(self.levelDir, '%s_old.json' % pureName(levelFn)),
        # 	oldLevelData)

        dumpJsonData(os.path.join(self.levelDir, levelFn), levelData)

    def doJob(self):
        if self.cmd == MetaCompatWorker.CMD_LIST:
            self.listUpgradeInfos()
        elif self.cmd == MetaCompatWorker.CMD_UPGRADE:
            self.upgradeLevelFiles()
        elif self.cmd == MetaCompatWorker.CMD_ATTACH_META:
            self.attachMeta()
        elif self.cmd == MetaCompatWorker.CMD_LIST_VALUE:
            self.listValues()
        elif self.cmd == MetaCompatWorker.CMD_VALUE_CHANGE:
            self.applyValueChange()

    def check(self, oldNodesDefData, nodesDefData):
        """
        对比老meta和新meta，提取他们之间的区别
        只增加节点时的情形，不需要处理
        """
        keysOld = set([node['name'][-1] for node in oldNodesDefData])
        keysNew = set([node['name'][-1] for node in nodesDefData])

        # 只有在old中才存在的节点集合
        keyOnlyInOld = keysOld - keysNew
        # 在两个集合中都存在的keys
        keysCommon = keysOld & keysNew

        return keyOnlyInOld, keysCommon

    def extractId2NameMapping(self, nodesDefData):
        """
        从元数据中抽取id->name的映射关系
        """
        id2Name = {}
        for node in nodesDefData:
            id2Name[node['name'][-1]] = node['name'][0]
            if len(node['args']) == 0:
                continue
            for arg in node['args']:
                id2Name[arg['name'][-1]] = arg['name'][0]
            for ret in node['returns']:
                id2Name[ret['name'][-1]] = ret['name'][0]

        return id2Name

    def listUpgradeInfos(self):
        """
        列出更新信息，但不对文件进行更新，由程序确定没有错误后，再进行更新
        """
        nodesDefData = loadJsonData('meta/nodes.json')
        levelFns = os.listdir(self.levelDir)

        id2Name = {}
        id2Name.update(self.extractId2NameMapping(nodesDefData))

        print('discovered following updates:')

        hasTypeChange = False
        changeTable = []

        for levelFn in levelFns:
            if not levelFn.endswith('.json') or levelFn.endswith('_old.json'):
                continue

            levelData = loadJsonData(os.path.join(self.levelDir, levelFn))

            levelMeta = levelData['meta']
            keysOnlyInOld, keysCommon = self.check(levelMeta, nodesDefData)
            id2Name.update(self.extractId2NameMapping(levelMeta))
            attrsUpdatePlans = self.attributeUpdatePlans(keysCommon, levelMeta, nodesDefData)
            print('%s:' % levelFn)
            if len(keysOnlyInOld) != 0:
                print('nodes removed')
                for nodeKey in keysOnlyInOld:
                    print(id2Name[nodeKey])
                print()

            if len(attrsUpdatePlans) != 0:
                for nodeKey in attrsUpdatePlans:
                    print('attr updates for node:', id2Name[nodeKey])
                    deletes = attrsUpdatePlans[nodeKey].get('deletes', [])
                    if len(deletes) != 0:
                        print('attribute deletes')
                        for attrKey in deletes:
                            print(id2Name[attrKey])
                        print()

                    adds = attrsUpdatePlans[nodeKey].get('adds', [])
                    if len(adds) != 0:
                        print('attribute adds')
                        for addEntry in adds:
                            print(id2Name[addEntry['attrId']], end=' ')
                            if 'default' in addEntry:
                                print(':', addEntry['default'])
                            else:
                                print()

                    updatePlans = attrsUpdatePlans[nodeKey].get('updates', [])
                    if len(updatePlans) != 0:
                        print('attribute updates')
                        for updatePlan in updatePlans:
                            for updateType in updatePlan['update_types']:
                                if updateType == 'add_default':
                                    print('add default value', updatePlan['new_default'], 'for attr',
                                          id2Name[updatePlan['attrId']])
                                elif updateType == 'delete_default':
                                    print('remove default value', updatePlan['old_default'], 'for attr',
                                          id2Name[updatePlan['attrId']])
                                elif updateType == 'update_default':
                                    print('update default value', updatePlan['old_default'], '->',
                                          updatePlan['new_default'], 'for attr', id2Name[updatePlan['attrId']])
                                elif updateType == 'type_change':
                                    hasTypeChange = True
                                    print('change type', updatePlan['old_type'], '->', updatePlan['new_type'],
                                          'for attr', id2Name[updatePlan['attrId']])
                                    changeTableEntry = {
                                        'level': levelFn,
                                        'old_type': updatePlan['old_type'],
                                        'new_type': updatePlan['new_type'],
                                        'attr_type': updatePlan['attrId'],
                                        'attr_name': id2Name[updatePlan['attrId']],
                                        'node_type': nodeKey,
                                        'node_name': id2Name[nodeKey]
                                    }
                                    # print 'before'
                                    self.fillWithAvailableValues(changeTableEntry, levelData)

                                    changeTable.append(changeTableEntry)
                        print()
                    print()

        if hasTypeChange:
            print('please refer type_change.py for more information')
            leadingString = """
# define your change functions like this
# def string2Int(strVal):
#     return int(strVal)
#
# def bool2String(boolVal):
#     return str(boolVal)
#
# then fill these function names to the following changeRule
# at last run: 
#        python MetaCompatChecker.py %s
# to apply the value change to all level files under graph directory
# original version of level are saved as level_xxx_old.json
""" % self.CMD_UPGRADE
            changeRuleString = json.dumps(changeTable, indent=4)
            with open('type_change.py', 'w') as f:
                f.write('%s\n\n' % leadingString)
                f.write('changeRule = ')
                f.write('%s\n' % changeRuleString)
        else:
            if os.path.exists('type_change.py'):
                os.remove('type_change.py')

    def upgradeLevelFiles(self):
        """
        对graph目录下，已经制作完成的level关卡文件，进行升级;
        依据最新的nodes.json定义
        """
        setUpLog('type_change')

        changeRuleMap = {}
        if os.path.exists('type_change.py'):
            import type_change
            changeRule = type_change.changeRule
            changeRuleMap = dict([(entry['level'], entry) for entry in changeRule])

        levelFns = os.listdir(self.levelDir)
        for levelFn in levelFns:
            if not levelFn.endswith('.json') or levelFn.endswith('_old.json'):
                continue

            changeRuleEntry = changeRuleMap.get(levelFn, None)
            if changeRuleEntry is None:
                self.upgradeLevelFile(levelFn, None, None)
            else:
                self.upgradeLevelFile(levelFn, changeRuleEntry, type_change)

    def upgradeLevelFile(self, levelFn, changeRuleEntry, module):
        """
        更新某个给定的level文件，
        :param levelFn: 节点文件名称
        :param nodeKeyOnlyInOld: 需要删除的节点key
        :param attrsUpdatePlans: 相同节点key，的节点属性更新计划
        :return:
        """
        logger = logging.getLogger('type_change')
        levelData = loadJsonData(os.path.join(self.levelDir, levelFn))
        levelMeta = levelData['meta']
        nodeKeyOnlyInOld, keysCommon = self.check(levelMeta, self.nodesDefData)
        attrsUpdatePlans = self.attributeUpdatePlans(keysCommon, levelMeta, self.nodesDefData)

        if len(attrsUpdatePlans) == 0 and len(nodeKeyOnlyInOld) == 0:
            return

        id2Type = dict([(node['id'], node['type']) for node in levelData['nodes']])
        id2Pos = dict([(node['id'], node['pos']) for node in levelData['nodes']])

        hasUpdates = False
        hasTypeChange = False
        if len(nodeKeyOnlyInOld) != 0:
            # 删除已经不用的节点，及其附带的边
            self.removeNodesAndEdges(nodeKeyOnlyInOld, levelData)
            hasUpdates = True

        newNodesData = []
        filterEdgesData = []

        # 对新老共有的节点，增删属性
        for node in levelData['nodes']:
            nodeKey = node['type']

            if nodeKey in attrsUpdatePlans:
                deletes = attrsUpdatePlans[nodeKey].get('deletes', [])
                addPlans = attrsUpdatePlans[nodeKey].get('adds', [])
                updatePlans = attrsUpdatePlans[nodeKey].get('updates', [])
                args = node['args']

                updatedArgs = {}

                for argKey in list(args.keys()):
                    if argKey in deletes:
                        hasUpdates = True
                        continue
                    updatedArgs[argKey] = args[argKey]

                for addPlan in addPlans:
                    if 'default' in addPlan:
                        hasUpdates = True
                        updatedArgs[addPlan['attrId']] = addPlan['default']

                for updatePlan in updatePlans:
                    updateTypes = updatePlan['update_types']
                    argKey = updatePlan['attrId']
                    for updateType in updateTypes:
                        if updateType == 'add_default':
                            # 如果对应属性没有赋值，且没有入边，将这个默认值加到level数据中
                            if argKey not in args and \
                                    not self.hasInEdge(levelData['edges'], node['id'], argKey):
                                updatedArgs[argKey] = updatePlan['new_default']
                        elif updateType == 'delete_default':
                            if argKey in updatedArgs and updatedArgs[argKey] == updatePlan['old_default']:
                                del updatedArgs[argKey]
                        elif updateType == 'update_default':
                            if argKey in args and args[argKey] == updatePlan['old_default']:
                                updatedArgs[argKey] = updatePlan['new_default']
                        elif updateType == 'type_change':
                            assert changeRuleEntry is not None, 'no change rule for %s' % levelFn
                            changeAttrType = changeRuleEntry['attr_type']
                            print('change attr', changeAttrType)
                            if changeAttrType in args:
                                # 被改变的数据具有参数值
                                handleFunc = getattr(module, changeRuleEntry['function'])
                                # args[changeAttrType] = handleFunc(args[changeAttrType])
                                updatedArgs[changeAttrType] = handleFunc(args[changeAttrType])
                                hasTypeChange = True
                            elif self.hasInEdge(levelData['edges'], node['id'], changeAttrType):
                                # 检查该属性是否有附带的边
                                # 有附带的边， 删除该边
                                filterEdgesData.append({
                                    'toId': node['id'],
                                    'toItemId': changeAttrType
                                })
                        hasUpdates = True

                node['args'] = updatedArgs
            newNodesData.append(node)

        # 对于已经删除的属性构成的边，要删除所有附带边
        newEdgesData = []
        for edge in levelData['edges']:
            # 检验出边
            startNodeKey = id2Type[edge['start']]
            startItemKey = edge['startItemId']
            if startNodeKey in attrsUpdatePlans:
                deletes = attrsUpdatePlans[startNodeKey].get('deletes', [])
                if startItemKey in deletes:
                    hasUpdates = True
                    continue

            # 检验入边
            endNodeKey = id2Type[edge['end']]
            endItemKey = edge['endItemId']
            if endNodeKey in attrsUpdatePlans:
                deletes = attrsUpdatePlans[endNodeKey].get('deletes', [])
                if endItemKey in deletes:
                    hasUpdates = True
                    continue

            isFiltered = False
            for feData in filterEdgesData:
                if feData['toId'] == edge['end'] and feData['toItemId'] == edge['endItemId']:
                    startPos, endPos = id2Pos[edge['start']], id2Pos[edge['end']]
                    msg = 'delete edge of %s, %s|%s (%.1f,%.1f) --> %s|%s (%.1f, %.1f)' % (levelFn,
                                                                                           edge['startNodeName'],
                                                                                           edge['startItemName'],
                                                                                           startPos['x'],
                                                                                           startPos['y'],
                                                                                           edge['endNodeName'],
                                                                                           edge['endItemName'],
                                                                                           endPos['x'],
                                                                                           endPos['y'])
                    isFiltered = True
                    logger.info(msg)
                    break

            if not isFiltered:
                newEdgesData.append(edge)

        if not hasUpdates:
            return

        levelData['nodes'] = newNodesData
        levelData['edges'] = newEdgesData

        if hasUpdates:
            metas = []
            usedNodeKeys = set([node['type'] for node in levelData['nodes']])
            for nodeDef in self.nodesDefData:
                if nodeDef['name'][-1] in usedNodeKeys:
                    metas.append(nodeDef)

            levelData['meta'] = metas

            # 将老文件进行备份，命名为XX_old.json
            # oldLevelData = loadJsonData(os.path.join(self.levelDir, levelFn))
            # dumpJsonData(os.path.join(self.levelDir, '%s_old.json' % pureName(levelFn)), oldLevelData)

            # 将levelData写入到文件中
            dumpJsonData(os.path.join(self.levelDir, levelFn), levelData)
            print('done', levelFn)

    def attributeUpdatePlans(self, keysCommon, oldNodesDefData, nodesDefData):
        """
        计算新老节点定义中，相同节点的属性区别，并计算更新计划
        """
        attrDiffs = {}

        oldNodesDefMap = dict([(node['name'][-1], node) for node in oldNodesDefData])
        nodesDefMap = dict([(node['name'][-1], node) for node in nodesDefData])

        for nodeKey in keysCommon:
            oldDefNode = oldNodesDefMap[nodeKey]
            newDefNode = nodesDefMap[nodeKey]
            oldArgsDefMap = dict([(arg['name'][-1], arg) for arg in oldDefNode['args']])
            argsDefMap = dict([(arg['name'][-1], arg) for arg in newDefNode['args']])

            diff = {}

            attrOnlyInOld, attrOnlyInNew, attrsCommon = self.checkAttribute(oldDefNode, newDefNode)
            if len(attrOnlyInOld) != 0:
                # 需要移除的属性
                diff['deletes'] = list(attrOnlyInOld)
            if len(attrOnlyInNew) != 0:
                diff['adds'] = []
                for argKey in attrOnlyInNew:
                    arg = argsDefMap[argKey]
                    if 'default' in arg:
                        diff['adds'].append({
                            'attrId': argKey,
                            'default': arg['default']
                        })
                    else:
                        diff['adds'].append({
                            'attrId': argKey
                        })

            # 检查属性的更新
            # 属性的更新包括：默认值的增加和删除，属性类型的变更
            argUpdatePlans = []
            for argKey in attrsCommon:
                oldArg = oldArgsDefMap[argKey]
                newArg = argsDefMap[argKey]
                updatePlan = {}
                updateTypes = []

                # 检查默认值的增加
                if 'default' in newArg and 'default' not in oldArg:
                    # 添加了默认值
                    updateTypes.append('add_default')
                elif 'default' in oldArg and 'default' not in newArg:
                    # 删除了默认值
                    updateTypes.append('delete_default')
                elif 'default' in oldArg and 'default' in newArg and oldArg['default'] != newArg['default']:
                    updateTypes.append('update_default')

                if oldArg['type'] != newArg['type']:
                    updateTypes.append('type_change')

                if len(updateTypes) == 0:
                    # argKey的这个属性没有发生变化，不列入更新计划
                    continue

                if 'default' in newArg:
                    updatePlan['new_default'] = newArg['default']
                if 'default' in oldArg:
                    updatePlan['old_default'] = oldArg['default']

                updatePlan['old_type'] = oldArg['type']
                updatePlan['new_type'] = newArg['type']
                updatePlan['update_types'] = updateTypes
                updatePlan['attrId'] = argKey
                argUpdatePlans.append(updatePlan)
            if len(argUpdatePlans) != 0:
                diff['updates'] = argUpdatePlans

            if len(diff) != 0:
                attrDiffs[nodeKey] = diff

        return attrDiffs

    def removeNodesAndEdges(self, keyOnlyInOld, levelData):
        """
        对于已经被删除的节点，需要在原levels中，
        将对应的这个类型的节点及其关联边一并删除
        """
        newLevelNodes = []
        newLevelEdges = []

        id2Type = dict([(node['id'], node['type']) for node in levelData['nodes']])

        for node in levelData['nodes']:
            if node['type'] in keyOnlyInOld:
                continue
            newLevelNodes.append(node)

        for edge in levelData['edges']:
            edgeStartKey = id2Type[edge['start']]
            edgeEndKey = id2Type[edge['end']]
            if edgeStartKey in keyOnlyInOld or edgeEndKey in keyOnlyInOld:
                continue
            newLevelEdges.append(edge)

        levelData['nodes'] = newLevelNodes
        levelData['edges'] = newLevelEdges

    def checkAttribute(self, oldDefNode, newDefNode):
        """
        检查老的定义节点和新的定义节点在属性上的区别
        """
        attrOld = set([arg['name'][-1] for arg in oldDefNode['args']])
        attrNew = set([arg['name'][-1] for arg in newDefNode['args']])

        attrOnlyInOld = attrOld - attrNew
        attrOnlyInNew = attrNew - attrOld
        attrsCommon = attrOld & attrNew

        return attrOnlyInOld, attrOnlyInNew, attrsCommon

    def hasInEdge(self, edgesData, nodeId, attrId):
        """
        检查nodeId所属的节点在属性attrId上，是否有入边
        """
        for edge in edgesData:
            if edge['end'] == nodeId and edge['endItemId'] == attrId:
                return True
        return False

    def fillWithAvailableValues(self, changeTableEntry, levelData):
        """
        在改变表中添加，每个改变项，可能的取值
        """
        # print json.dumps(changeTableEntry)
        for node in levelData['nodes']:
            availValues = []
            args = node['args']
            for argKey in args:
                if argKey == changeTableEntry['attr_type']:
                    availValues.append(args[argKey])
            if 'avail_values' in changeTableEntry:
                changeTableEntry['avail_values'].extend(availValues)
            else:
                changeTableEntry['avail_values'] = availValues

        changeTableEntry['avail_values'] = list(set(changeTableEntry['avail_values']))
        changeTableEntry['function'] = """ type your function name here """

    def listValues(self):
        if not os.path.exists('value_change.in'):
            print('no value_change.in file exists')
            return

        queryData = loadJsonData('value_change.in')
        avail_valuesList = []
        for entry in queryData:
            opt_filenames = entry['files']
            avail_values = []
            for fn in opt_filenames:
                fullname = os.path.join(self.levelDir, fn)
                if not os.path.exists(fullname):
                    continue
                levelData = loadJsonData(fullname)
                nodesData = levelData['nodes']
                for node in nodesData:
                    if node['type'] != entry['node_type']:
                        continue
                    args = node['args']
                    if entry['attr_type'] in args:
                        avail_values.append(args[entry['attr_type']])
            entry['avail_values'] = list(set(avail_values))
            entry['function'] = ' type your function here '
        # avail_valuesList.append(avail_values)

        print('please refer value_change.py for more information')
        leadingString = """
# define your change functions like this
# def int2OtherInt(intVal):
#     return intVal*100
#
# def string2OtherString(strVal):
#     return strVal + '-1'
#
# then fill these function names to the following changeRule
# at last run: 
#        python MetaCompatChecker.py -c %s -d <levelDir>
# to apply the value change to all level files under graph directory
""" % self.CMD_VALUE_CHANGE
        changeRuleString = json.dumps(queryData, indent=4)
        with open('value_change.py', 'w') as f:
            f.write('%s\n\n' % leadingString)
            f.write('changeRule = ')
            f.write('%s\n' % changeRuleString)

    def applyValueChange(self):
        if not os.path.exists('value_change.py'):
            print('no value_change.py file exists')
            return

        import value_change
        changeRule = value_change.changeRule
        for entry in changeRule:
            for fn in entry['files']:
                fullname = os.path.join(self.levelDir, fn)
                if not os.path.exists(fullname):
                    continue

                levelData = loadJsonData(fullname)
                nodesData = levelData['nodes']
                hasUpdates = False
                for node in nodesData:
                    if node['type'] != entry['node_type']: continue
                    args = node['args']
                    attrType = entry['attr_type']
                    if attrType in args:
                        handleFunc = getattr(value_change, entry['function'])
                        args[attrType] = handleFunc(args[attrType])
                        hasUpdates = True

                if hasUpdates:
                    dumpJsonData(fullname, levelData)
                    print('update ', fn)


def main():
    parser = argparse.ArgumentParser(description='batch processing of level files',
                                     prog='python MetaCompatChecker.py')
    parser.add_argument('-d', '--leveldir', help='directory of level files.')
    cmd_opts = [MetaCompatWorker.CMD_LIST, MetaCompatWorker.CMD_UPGRADE,
                MetaCompatWorker.CMD_ATTACH_META, MetaCompatWorker.CMD_LIST_VALUE,
                MetaCompatWorker.CMD_VALUE_CHANGE]
    parser.add_argument('-c', '--command', choices=cmd_opts,
                        required=True,
                        help='command to execute')

    args = parser.parse_args()
    # print args
    if args.leveldir is not None:
        levelDir = args.leveldir
        if ':' in levelDir or levelDir.startswith('/'):
            pass
        else:
            levelDir = os.path.join(os.getcwd(), levelDir)

        metaWorker = MetaCompatWorker(cmd=args.command, levelDir=levelDir)
        metaWorker.doJob()
    else:
        metaWorker = MetaCompatWorker(cmd=args.command)
        metaWorker.doJob()


if __name__ == '__main__':
    main()
