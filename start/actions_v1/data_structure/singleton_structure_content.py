# -*- coding: utf-8 -*-
import sys, os

sys.path.append(os.path.dirname(__file__))


global_config = None
global_meta = None

def set_config(config):
	global global_config
	assert global_config is None
	global_config = config

def set_config_path(config_path):
	import json
	with open(config_path, encoding='utf-8') as f:
		config = json.load(f)
		set_config(config['data'])

def new_content():
	global global_meta, global_config
	if global_config is None:
		import os
		set_config_path(os.path.join(os.path.dirname(__file__), 'config/dialysis_fields.json'))
	if global_meta is None:
		from meta_info import TreeMetaInfo
		meta = TreeMetaInfo()
		meta.init(global_config)
		global_meta = meta
	from data_tree import DataTree
	return DataTree(global_meta)

if __name__ == '__main__':
	import pprint

	data = [{
		'zhuyuan': [{
			30101: '张三',
			30102: '时间1',
			30129: '入院时间1',
			30133: '入院诊断1',
			30131: '出院时间1',
			'chrujilu': [{
				30181: '主要',
				30134: '受伤',
			}, {
				30181: '次要',
				30134: '生病'
			}
			],
			'ssjl': [{
				30145: 'A',
				30146: 'B'
			}]
		}, {
			30101: '张三',
			30102: '时间2',
			'chrujilu': [{
				30181: '主要'
			}, {
				30181: '次要'
			}
			],
			'ssjl': [{
				30145: 'A',
				30146: 'B'
			}]
		}
		]
	},
		{
			'zhuyuan': [{
				30101: '张三',
				30102: '时间3',
				30129: '入院时间2',
				30133: '入院诊断2',
				'chrujilu': [{
					30181: '主要'
				}, {
					30181: '次要',
					30134: '惊吓'
				}
				],
				'ssjl': [{
					30145: 'A',
					30146: 'B'
				}]
			}, {
				30101: '张三',
				30102: '时间4',
				'chrujilu': [{
					30181: '主要'
				}, {
					30181: '次要'
				}
				],
				'ssjl': [{
					30145: 'A',
					30146: 'B'
				}]
			}
			]
		}
	]

	content = new_content()
	content.push_group(data)
	pprint.pprint(content.export())
