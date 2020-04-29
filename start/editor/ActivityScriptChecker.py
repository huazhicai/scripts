# -*- coding:utf-8 -*-

import os
import sys
import json

sys.path.append('./output/common')
sys.path.append('./output/server')
sys.path.append('./output/client')
# from SceneSocket.ParseSceneSocket import chunk_size_map
# from SceneSocket.SceneSoketReader import load_scene_sockets_pos_and_chunksize


class CheckRule(object):
    def __init__(self, checkList):
        self.checkList = checkList

        self.level_tile = {}  # level_script to tileinfo
        self.socket_data = None

        # load all nodes
        allNodePath = r'../main/meta/nodes.json'
        f = open(allNodePath, 'rb')
        nodes = json.load(f)
        self.type2Name = {}
        for node in nodes:
            info = node['name']
            self.type2Name[info[1]] = info[0]

    def _getAllSceneSocket(self, res_path, py_path):
        # copy from ParseSceneSocket
        scene_path = res_path + "/scene"
        sockets_data = {}
        for root, subdirs, files in os.walk(scene_path):
            for filename in files:
                fullname = os.path.join(root, filename)
                if os.path.isfile(fullname) and fullname.endswith('.scn'):
                    socketspos, chunk_size = load_scene_sockets_pos_and_chunksize(res_path, fullname)
                    fullname = fullname.replace('\\', '/')
                    filename = fullname.split('/res/')[1]
                    if socketspos is not None:
                        sockets_data[filename] = socketspos
                    if chunk_size is not None:
                        chunk_size_map[filename] = chunk_size

        flag_str = "_content/"
        tmp_data = {}
        for filename, data in list(sockets_data.items()):
            if filename.find(flag_str) != -1:
                tmp_data[filename] = data

        for filename, data in list(tmp_data.items()):
            del sockets_data[filename]
            scenename = filename[0:filename.index(flag_str)]
            scenename = "%s.scn" % scenename

            chunk_size = chunk_size_map.get(scenename, None)
            if chunk_size is not None:
                s = filename[filename.rindex('/') + 1:filename.rindex('.')]
                strs = s.split('_')
                idx_x, idx_z = int(strs[0]), int(strs[1])
                for name, socket_data in list(data.items()):
                    posstr = socket_data['pos']
                    posstrs = posstr.split(',')
                    posx, posy, posz = float(posstrs[0]), float(posstrs[1]), float(posstrs[2])
                    posx += idx_x * chunk_size
                    posz += idx_z * chunk_size
                    socket_data['pos'] = "%f,%f,%f" % (posx, posy, posz)

            target_data = sockets_data.get(scenename, None)
            if target_data is None:
                sockets_data[scenename] = data
            else:
                target_data.update(data)
        return sockets_data

    def _getNodeInfoById(self, level_script, node_id):
        for node in level_script['nodes']:
            if node['id'] == node_id:
                return node
        print(('\tError, not find %s' % node_id))
        return None

    def _findLinkInfo(self, cur_node, end, level_script):
        ret = set()
        edges = level_script['edges']
        for edge in edges:
            if edge['end'] == cur_node['id'] and edge['endItemId'] == end:
                start_node = self._getNodeInfoById(level_script, edge['start'])
                # Get String Variable
                print(('\t\t\tnode id:%s, node type:%s' % (start_node['id'], start_node['type'])))
                if start_node['type'] == 'e7c58b26-c80d-4617-b6ad-ea4ad191ec77':
                    strName = start_node['args']['8805aad9-80ab-458f-bb0f-d608867134f9']
                    # Find all Set String Variable with the same name
                    for node in level_script['nodes']:
                        if node['type'] == '8ff972bb-dec2-4184-b99a-7ee93476bc65' and \
                                node['args']['b250bcdf-6bf1-49f0-822d-862425605f17'] == strName:
                            ret = ret | self._findLinkInfo(node, '54949294-0625-49b5-a93d-bfafa37bd3b3', level_script)
                # Random Select String
                elif start_node['type'] == 'a6bfe777-df7c-484c-b16d-71259527dca4':
                    ret = ret | self._findLinkInfo(start_node, '95a121aa-3a18-4c7b-bbe6-02e6953e753b', level_script)
                elif start_node['type'] == '3dc4ecdb-0f17-4a01-9208-fa2caee0a217':
                    ret = ret | self._findLinkInfo(start_node, 'f1c40cbd-73e8-469c-afde-0375398a510c', level_script)
                # Get Array Element (String)
                elif start_node['type'] == '5ff25c22-aea0-4009-bc0c-fc0f727ffd1e':
                    ret = ret | self._findLinkInfo(start_node, '28a7ec94-7334-405d-a38e-ebc494da16f7', level_script)
                # Get Variable
                elif start_node['type'] == '11c2da9b-061a-4886-addf-fb4cf0e31789':
                    strNameSet = self._findLinkInfo(start_node, 'b39acaf1-8a0e-4a4b-a5ea-e1349dbc53ed', level_script)
                    for node in level_script['nodes']:
                        # find Set Variable with same name
                        if node['type'] == '7532929c-3d5e-4264-92cc-7f0b5c7ca0b7' and \
                                node['args']['5a87ff6a-01b4-4174-b617-d16fb06055ac'] in strNameSet:
                            ret = ret | self._findLinkInfo(node, '17ddb382-4d7f-47b4-a1f1-929bd74cf91e', level_script)
                # Shuffle Array
                elif start_node['type'] == 'a0aac12d-44b0-4191-99d4-920dbe750fac':
                    ret = ret | self._findLinkInfo(start_node, '96418872-85a8-4fff-87ab-64f6c5959aeb', level_script)
                # Array Data(String)
                elif start_node['type'] == '400d6243-58e4-43e1-a1fc-34fa41a421ff':
                    ret = ret | self._findLinkInfo(start_node, 'eacc0cc7-ff58-493a-9b7b-bb2f27fe44a7', level_script)
                else:
                    raise NotImplementedError
                return self._processMultiValue(ret)

        # here we need get value according to type of args
        ret.add(cur_node['args'].get(end, None))
        return ret

    def _processMultiValue(self, set_value):
        ret = set()
        for values in set_value:
            if values:
                for value in values.split(','):
                    ret.add(value.strip())
        return ret

    def checkMarkpoint(self, level_template_id, level_script, node, check_rule):
        print(('\tIn checking node %s, id %s' % (self.type2Name[node['type']], node['id'])))
        if not self.socket_data:
            cur_path = '.'
            if os.path.isdir(sys.path[0]):
                cur_path = sys.path[0]
            elif os.path.isfile(sys.path[0]):
                cur_path = os.path.dirname(sys.path[0])
            resPath = cur_path + "/../../../client/src/Resources/res"
            pyPath = cur_path + "/output"
            self.socket_data = self._getAllSceneSocket(resPath, pyPath)
        import level_template
        import level_tile
        if level_template_id not in list(self.level_tile.keys()):
            self.level_tile[level_template_id] = {}
            tiles = level_template.data[level_template_id]['tiles']
            for tile in tiles:
                # not consider tile_index is None
                self.level_tile[level_template_id][tile.get('tile_index', None)] = level_tile.data[tile['tile_name']][
                    'model_path']

        tileindexDict = self.level_tile[level_template_id]

        tileindexSet = self._findLinkInfo(node, check_rule[0], level_script)
        socketnameSet = self._findLinkInfo(node, check_rule[1], level_script)

        for tileindex in tileindexSet:
            model_path = tileindexDict.get(tileindex, None)
            if not model_path:
                print(('\t\tnot find tile %s' % (tileindex)))
                continue
            for socketname in socketnameSet:
                if not socketname:
                    print('\t\t\t Spawn or block point is None')
                    continue
                if socketname not in list(self.socket_data[model_path].keys()):
                    print(("\t\t %s:%s not find" % (str(tileindex), str(socketname))))


CheckList = {
    # node type : checkrule list
    # Create Monster
    'b8bdb1c4-48e3-4c7b-b38e-12aef4a29db0':
        [('66e88998-31a7-46fd-9f54-65c5dc2a78e8', '33228f1d-1b7a-405d-82d4-7958acc8e8dc', 'checkMarkpoint'), ],
    # Create Monster Boss
    'f7454550-56f5-4242-86a8-9e46b140feab':
        [('4a459fe3-7963-4bcb-acd6-a0372a1ee9a3', '8b062406-a831-4a43-baad-9c7bd65a84ef', 'checkMarkpoint'), ],
    # Create NPC
    '83e7076d-9d00-4415-9e9f-d121c6d0d2e6':
        [('9d1e7f79-a2eb-459c-81da-a3014a8924c3', '7032826b-37c5-4299-a172-2621c92ef289', 'checkMarkpoint'), ],
    # Move Unit
    '8353b9db-48ef-42bb-9d61-5752bb14ce5e':
        [('3082f47b-5438-4697-be6f-16cd5f57fc91', '85705aa7-ecfc-4b37-a95b-423cb42368e8', 'checkMarkpoint'), ],
    # Create Mechanism
    'f0f220b5-e584-4aff-8c86-f039d030c02b':
        [('bb186896-158c-4956-9962-692ad0d4193f', 'b84f6f5c-695f-4b56-b98b-3bd61698bd3c', 'checkMarkpoint'),
         ('bb186896-158c-4956-9962-692ad0d4193f', 'ef2c9f0a-4342-40d0-9c45-b09ca8ad1545', 'checkMarkpoint'),
         ],
    # AI Patrol Path
    '6d069566-54d8-4718-8b9a-c6fdb7120443':
        [('663b432a-7334-44cb-a88d-9f228c3aeab7', '2ca86bb7-4a82-4a3b-b1fd-bb33230243ba', 'checkMarkpoint'), ],
    # Transport Unit to
    '236ec09a-fe30-45eb-ad16-eb47429b334e':
        [('4cb06366-5950-4971-9358-18133a94630d', 'b7ae3ff7-373d-4efc-8678-74d63edfb2f9', 'checkMarkpoint'), ],
    # Auto Create Player Unit
    '02b886bc-365f-4913-bae0-3dbf270633f3':
        [('02f22f37-2c83-45b6-bdad-70f29d142acb', 'f0be1ac7-0a80-4081-84ea-00ac3d824dad', 'checkMarkpoint'), ],
}


class Checker(object):
    def __init__(self, checkRule):
        self.checkRule = checkRule

    def checkAll(self, out_put_path):
        # partly copy from UsedSceneSocket
        import level_config
        for level_info in list(level_config.data.values()):
            for level_script_module in [level_info.get('level_script'), level_info.get('client_level_script')]:
                if level_script_module is None:
                    continue
                # if level_script_module != 'level_354':
                #	continue
                print(('Checking %s' % level_script_module))
                level_template_id = level_info['level_template']
                path_dict = {}
                f = open(out_put_path + '/../levelscripts/' + level_script_module + '.json', 'rb')
                level_script = json.load(f)
                nodes = level_script['nodes']

                for node_info in nodes:
                    checkList = self.checkRule.checkList.get(node_info['type'], [])
                    for checkrule in checkList:
                        getattr(self.checkRule, checkrule[-1])(level_template_id, level_script, node_info, checkrule)


if __name__ == '__main__':
    checkRules = CheckRule(CheckList)
    checker = Checker(checkRules)

    out_put_path = './output'
    checker.checkAll(out_put_path)
