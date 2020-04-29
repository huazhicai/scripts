import os
import subprocess

config_data = {
    'nodes': [{'event_actions': {'Default': 'Start'}, 'event_links': {'Out': {1: 'In'}}, 'inputs': {}, 'outputs': {}},
              {'event_actions': {'In': 'RequestUrl'}, 'event_links': {'Out': {2: 'In'}}, 'inputs': {'url_str': 10},
               'outputs': {'response_str': 0}}, {'event_actions': {'In': 'ParseUrl'}, 'event_links': {'Out': {3: 'In'}},
                                                 'inputs': {'page_source_str': 0, 'xpath_str': 11},
                                                 'outputs': {'result_list': 1}},
              {'event_actions': {'In': 'IteratorList'}, 'event_links': {'Out': {4: 'In'}}, 'inputs': {'doc_list': 1},
               'outputs': {'item_any': 2}},
              {'event_actions': {'In': 'StringConcat'}, 'event_links': {'Out': {5: 'In', 12: 'In'}},
               'inputs': {'prefix_str': 12, 'suffix_str': 2}, 'outputs': {'contacted_str': 3}},
              {'event_actions': {'In': 'RequestUrl'}, 'event_links': {'Out': {6: 'In'}}, 'inputs': {'url_str': 3},
               'outputs': {'response_str': 4}}, {'event_actions': {'In': 'ParseUrl'}, 'event_links': {'Out': {7: 'In'}},
                                                 'inputs': {'page_source_str': 4, 'xpath_str': 13},
                                                 'outputs': {'result_list': 5}},
              {'event_actions': {'In': 'IteratorList'}, 'event_links': {'Out': {8: 'In'}}, 'inputs': {'doc_list': 5},
               'outputs': {'item_any': 6}},
              {'event_actions': {'In': 'StringConcat'}, 'event_links': {'Out': {9: 'In', 13: 'In'}},
               'inputs': {'prefix_str': 14, 'suffix_str': 6}, 'outputs': {'contacted_str': 7}},
              {'event_actions': {'In': 'RequestUrl'}, 'event_links': {'Out': {10: 'In'}}, 'inputs': {'url_str': 7},
               'outputs': {'response_str': 8}},
              {'event_actions': {'In': 'ParseUrl'}, 'event_links': {'Out': {11: 'In'}},
               'inputs': {'page_source_str': 8, 'xpath_str': 15}, 'outputs': {'result_list': 9}},
              {'event_actions': {'In': 'ConsoleOutput'}, 'event_links': {}, 'inputs': {'result_any': 9}, 'outputs': {}},
              {'event_actions': {'In': 'ConsoleOutput'}, 'event_links': {}, 'inputs': {'result_any': 3}, 'outputs': {}},
              {'event_actions': {'In': 'ConsoleOutput'}, 'event_links': {}, 'inputs': {'result_any': 7},
               'outputs': {}}],
    'runtime_data': [None, None, None, None, None, None, None, None, None, None, 'https://www.pumch.cn/doctors.html',
                     '//*[@id="m1"]/div/div[2]/div/div/div[1]/a/@href', 'https://www.pumch.cn',
                     '//*[@id="datalist"]/div[1]/div/a/@href', 'https://www.pumch.cn',
                     '/html/body/div[5]/div[2]/div/div[2]/div[1]/div[1]/text()'], 'roots': [0]}


obj_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'crawler_graph', 'run.py')
# print(obj_file)
proc = subprocess.Popen(["python3", obj_file, str(config_data)], shell=True, stdout=subprocess.PIPE)
# try:
#     outs, errs = proc.communicate(timeout=15)
#     print(outs)
# except subprocess.TimeoutExpired:
#     proc.kill()
#     outs, errs = proc.communicate()
# p1 = subprocess.run(["python3", obj_file, str(config_data)], capture_output=True)
print(proc.stdout.read())
# print(proc.communicate())
