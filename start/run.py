# -*- coding: utf-8 -*-
import argparse
import sys, os
import json

from GenNodes import GenerateNodes

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'editor'))
from editor import main


def parsearg():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--nodes", help="auto generate nodes", action='store_true')
    parser.add_argument("-f", "--file", help="run graphics with json file", type=str, action='store')
    parser.add_argument('-a', "--arg", help="external arguments of json file", type=dict, action='store')
    parser.add_argument('-e', "--editor", help="open node editor", action='store_true')
    arg = parser.parse_args()
    return arg


def run():
    arg = parsearg()
    if arg.nodes:
        filename = 'editor/meta/nodes.json'
        generater = GenerateNodes()
        generater.save_to_json(filename)
    elif arg.file and os.path.exists(arg.file):
        from editor.A_Exporter import single_file_export

        filename = arg.file
        data = read_graph_file(filename)
        graph_config = single_file_export(data)
        input_args = arg.arg if arg.arg else {}

        crawl(graph_config, input_args=input_args)  # 调用json 文件运行
    else:
        main.main()


def read_graph_file(file):
    with open(file) as f:
        data = json.load(f)
    return data


def crawl(graph_config, pipe_conn=None, input_args=None):
    from runtime.Runtime import GraphRunnerInstance
    instance = GraphRunnerInstance(pipe_conn)
    instance.run_graph(graph_config, input_args)

    if pipe_conn:
        pipe_conn.send('finished')


# def run(argv):
#     if len(argv) < 2:
#         main.main()  # 运行编辑器
#     else:
#         filename = argv[1]
#         if filename == 'nodes':
#             filename = 'editor/meta/nodes.json'
#             generater = GenerateNodes()
#             generater.save_to_json(filename)
#
#         else:
#             data = read_graph_file(filename)
#             from editor.A_Exporter import single_file_export
#             graph_config = single_file_export(data)
#             args = {}
#             if len(argv) > 2:
#                 values = argv[2].strip(' {}').split(',')
#                 for item in values:
#                     k, v = item.split(':')
#                     k.strip()
#                     v.strip()
#                     args[k] = v
#             crawl(graph_config, input_args=args)  # 调用json 文件运行


def run_file(filename, input_args=None):
    data = read_graph_file(filename)
    from editor.A_Exporter import single_file_export
    graph_config = single_file_export(data)
    crawl(graph_config, input_args=input_args)


if __name__ == "__main__":
    # print(sys.argv)
    # run(sys.argv)
    run()
