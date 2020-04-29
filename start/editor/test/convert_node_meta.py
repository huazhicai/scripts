# coding:utf-8

import json
import uuid
import data


def convert_file():
    nodes_data = data.load_nodes_meta_information()
    for node_data in nodes_data:
        name = node_data['name']
        node_data['name'] = [name, str(uuid.uuid1())]
        if node_data.get('args', None) is not None and len(node_data['args']) != 0:
            for arg in node_data['args']:
                arg_name = arg['name']
                arg['name'] = [arg_name, str(uuid.uuid1())]

        if node_data.get('returns', None) is not None and len(node_data['returns']) != 0:
            for ret in node_data['returns']:
                ret_name = ret['name']
                ret['name'] = [ret_name, str(uuid.uuid1())]

    f = open('/Users/mac/PycharmProjects/crawler/edit/meta/nodes.json', 'w')
    json.dump(nodes_data, f, indent=4)
    f.close()


if __name__ == '__main__':
    convert_file()
