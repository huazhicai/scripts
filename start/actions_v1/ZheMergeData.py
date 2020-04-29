from datetime import datetime

from runtime.Action import Action
from actions.data_structure.singleton_structure_content import new_content, set_config_path


class InitConfig(Action):
    _id = '9ed37096-bc78-47c9-b0d0-12acjvl345622d'
    node_info = {"args": [['file_path', 'String', '12325418-e9a4-11e9-9dd5-f4523145acec'],
                          ['In', 'Event', 'e7253154-e9a4-11e9-bc41-f432541254ec']
                          ],
                 "returns": [['Out', 'Event', '123568ac-e9a4-11e9-ba9b-f6325a27acec']]}

    def __call__(self, args, io):
        file_path = args['file_path']
        set_config_path(file_path)
        io.push_event('Out')


class ExtractData(Action):
    _id = '9ed37096-bc78-47c9-b0d0-663jalcldkc22d'
    node_info = {"args": [['data_source', 'List', 'e1421acd-e9a4-11e9-9dd5-f4523145acec'],
                          ['priority_key', 'Int', '12345687-e9a4-11e9-9dd5-f4523145acec'],
                          ['In', 'Event', 'eajcl3870-e9a4-11e9-bc41-f432541254ec']
                          ],
                 "returns": [['content', 'Any', '23156af31-e9a4-11e9-bb0d-f416630aacec'],
                             ['Out', 'Event', 'e2315472-e9a4-11e9-ba9b-f6325a27acec']]}

    def time_to_stamp(self, val):
        if isinstance(val, datetime):
            return val.timestamp()
        elif isinstance(val, str):
            val = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
            return val.timestamp()
        else:
            return 0

    def put_val(self, doc, content):
        for key, val in doc:
            if isinstance(val, list):
                for item in val:
                    self.put_val(item, content)
            elif isinstance(val, dict):
                self.put_val(val, content)
            elif val:
                pri = self.time_to_stamp(val) if key == self.priority else 0
                if key in self.seen:
                    content.push_source(key, val, True, priority=pri)
                else:
                    content.push_source(key, val, priority=pri)

    def __call__(self, args, io):
        data_source = args['data_source']
        priority_key = args['priority_key']
       
        content = new_content()
        if priority_key:
            content.push_group(data_source, priority_key=priority_key)
        else:
            content.push_group(data_source)
        
        io.set_output('content', content)
        io.push_event('Out')


class DataMerge(Action):
    _id = '9ed37096-bc78-47c9-b0d0-6632231456122d'
    node_info = {"args": [['content1', 'Any', '95acjvl-e9a4-11e9-9dd5-f4523145acec'],
                          ['content2', 'Any', '95acjvl-e9a4-11e9-9dd5-f521436acjal'],
                          ['In', 'Event', 'e123258ac-e9a4-11e9-bc41-f432541254ec']
                          ],
                 "returns": [['content', 'Any', '9521ac-e9a4-11e9-9dd5-f521436acjal'],
                             ['Out', 'Event', '2315487a-e9a4-11e9-ba9b-f6325a27acec']]}

    def __call__(self, args, io):
        content1 = args['content1']
        content2 = args['content2']

        content1.merge(content2)

        io.set_output('content', content1)
        io.push_event('Out')


class NormalizeData(Action):
    _id = '9ed37096-bc78-47c9-b0d0-66ajclvdej22d'
    node_info = {"args": [['content', 'Any', '95acjvl-e9a4-11e9-9dd5-aclanvecec'],
                          ['In', 'Event', 'e765213d0-e9a4-11e9-bc41-f432541254ec']
                          ],
                 "returns": [['data', 'Dict', '9564421-e9a4-11e9-9dd5-f521436acjal'],
                             ['Out', 'Event', 'e7102f42-e9a4-2315-ba9b-f6325a27acec']]}

    def __call__(self, args, io):
        content = args['content']

        content.normalize()

        io.set_output('data', content.export())
        io.push_event('Out')


