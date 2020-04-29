from runtime.Action import Action
import pymssql


class ConnectSQLServer(Action):
    """连接SQL Server数据库"""
    _id = '07bca6b8-ff66-11e9-b668-8cec4bd83f9f'
    node_info = {"args": [['host_str', 'String', 'd8881382-003a-11ea-b9ad-8cec4bd83f9f'],
                          ['port_int', 'Int', 'd8881383-003a-11ea-96f3-8cec4bd83f9f'],
                          ['user_str', 'String', 'd8881384-003a-11ea-b245-8cec4bd83f9f'],
                          ['password_str', 'String', 'd8881385-003a-11ea-9d1d-8cec4bd83f9f'],
                          ['database_str', 'String', 'd8881386-003a-11ea-88b4-8cec4bd83f9f'],
                          ['charset_str', 'String', 'd8881387-003a-11ea-b283-8cec4bd83f9f'],
                          ['In', 'Event', 'd8881388-003a-11ea-87cd-8cec4bd83f9f']],
                 "returns": [['connect', 'Any', 'd8881389-003a-11ea-bebf-8cec4bd83f9f'],
                             ['Out', 'Event', 'd888138a-003a-11ea-9add-8cec4bd83f9f']]}

    def __call__(self, args, io):
        host = args['host_str']
        port = args['port_int']
        user = args['user_str']
        password = args['password_str']
        database = args['database_str']
        charset = args['charset_str']
        if charset:
            connect = pymssql.connect(host=host, port=port, user=user, password=password,
                                      database=database, charset=charset)
        else:
            connect = pymssql.connect(host=host, port=port, user=user, password=password,
                                      database=database)
        if connect:
            print("连接成功")
        else:
            print("连接失败")
        io.set_output('connect', connect)
        io.push_event('Out')


class FetchSQLServerData(Action):
    """获取sql server数据"""
    _id = '15bffa1e-ff66-11e9-877e-8cec4bd83f9f'
    node_info = {"args": [['table_str', 'String', 'd888138b-003a-11ea-8d68-8cec4bd83f9f'],
                          ['field_list', 'List', 'd888138c-003a-11ea-bb95-8cec4bd83f9f'],
                          ['connect', 'Any', 'd888138d-003a-11ea-a8d1-8cec4bd83f9f'],
                          ['In', 'Event', 'd888138e-003a-11ea-9b0e-8cec4bd83f9f']],
                 "returns": [['data_list', 'List', 'd888138f-003a-11ea-9a43-8cec4bd83f9f'],
                             ['Out', 'Event', 'd8881390-003a-11ea-a3bf-8cec4bd83f9f']]}

    def __call__(self, args, io):
        table = args['table_str']
        fields = args['field_list']
        connect = args['connect']
        cursor = connect.cursor()

        out_data = []
        if fields:
            place_holder = ['%s' for i in range(len(fields))]
            place_holder = ', '.join(place_holder)
            sql = 'select top 30' + place_holder % tuple(fields) + ' from %s' % table

            cursor.execute(sql)
            row = cursor.fetchone()
            while row:
                temp = dict((fields[i], row[i])
                            for i in range(len(fields)))
                out_data.append(temp)
                row = cursor.fetchone()

        connect.close()
        io.set_output('data_list', out_data)
        io.push_event('Out')


class GetSQLServerData(Action):
    _id = '15bffa1e-f416-11e9-877e-8cec4bd75f9f'
    node_info = {"args": [['sql_statement', 'String', 'd8881391-003a-11ea-bd46-8cec4bd83f9f'],
                          ['connect', 'Any', 'd8881392-003a-11ea-ae94-8cec4bd83f9f'],
                          ['In', 'Event', 'd8881393-003a-11ea-a93b-8cec4bd83f9f']],
                 "returns": [['output_data', 'List', 'd8881394-003a-11ea-9372-8cec4bd83f9f'],
                             ['Out', 'Event', 'd8881395-003a-11ea-a110-8cec4bd83f9f']]}

    def __call__(self, args, io):
        sql_statement = args['sql_statement']
        connect = args['connect']
        cursor = connect.cursor()

        out_data = []
        if sql_statement:
            cursor.execute(sql_statement)
            row = cursor.fetchone()
            while row:
                # print(row)
                out_data.append(row)
                row = cursor.fetchone()

        io.set_output('output_data', out_data)
        io.push_event('Out')


class ConditionSQLServerData(Action):
    _id = '15bffa1e-f416-11e9-877e-8cec4bd349vf'
    node_info = {"args": [['sql_statement', 'String', 'd8881391-003a-11ea-bd46-8ceclkjdkjf5d9f'],
                          ['value', 'Any', 'd834nv91-003a-11ea-bd46-8ceclkjdkjf5d9f'],
                          ['connect', 'Any', 'd8jn2352-003a-11ea-ae94-8cec4bd83f9f'],
                          ['In', 'Event', 'd8881393-003a-11ea-a93b-8ce5214v3f9f']],
                 "returns": [['output_data', 'List', 'd88ackt44-003a-11ea-9372-8cec4bd83f9f'],
                             ['Out', 'Event', 'd7unv495-003a-11ea-a110-8cec4bd83f9f']]}

    def __call__(self, args, io):
        sql_statement = args['sql_statement']
        value = args['value']
        connect = args['connect']
        cursor = connect.cursor()

        out_data = []
        if sql_statement and value:
            cursor.execute(sql_statement % value)
        elif sql_statement and not value:
            cursor.execute(sql_statement)

        row = cursor.fetchone()
        while row:
            # print(row)
            out_data.append(row)
            row = cursor.fetchone()

        io.set_output('output_data', out_data)
        io.push_event('Out')


class CloseSQLserver(Action):
    _id = '4781b498-117d-11ea-b823-8cec4bd887f3'
    node_info = {"args": [['connect', 'Any', '94a9de98-117d-11ea-9648-8cec4bd887f3'],

                          ['In', 'Event', 'a63255dc-117d-11ea-9ea0-8cec4bd887f3']],
                 "returns": []}

    def __call__(self, args, io):
        connect = args['connect']
        connect.close()


class GetOracle8Data(Action):
    _id = '84771bb0-d65d-4640-99a9-7ed1221ccf99'
    node_info = {
        "args": [
            ['url', 'String', '9b9c995d-2804-4af8-a265-5594b36c6f06'],
            ['usr', 'String', '25baa98c-217b-49aa-85a0-8f718d66f2cc'],
            ['pwd', 'String', 'ffffcdae-efad-451e-96bd-8f0bd646b0b5'],
            ['sql', 'String', '1e06788f-348b-454f-ad18-8d1f46b4b941'],
            ['In', 'Event', '1ee7a3fc-5da1-4841-a271-5dd3c08da940']],
        "returns": [
            ['output_data', 'List', 'c0405f12-3796-40b9-8e58-498fb0fe1eef'],
            ['Out', 'Event', 'c129ef68-af81-4963-a38a-167e6dfa219b']]
    }

    def capital_to_lower(self, doc):
        new = {}
        for key, value in doc.items():
            new[key.lower()] = value
        return new

    def __call__(self, args, io):
        import subprocess, os, json, re
        curdir = os.path.split(os.path.realpath(__file__))[0]
        cmd = '"{}/../jre1.2/bin/java.exe" -classpath "{}/../oracle";"{}/../oracle/classes12.zip" OracleCon {} {} {} "{}"' \
            .format(curdir, curdir, curdir, args['url'], args['usr'], args['pwd'], args['sql'])
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = p.communicate()
       
        # try:
        output = eval(str(stdout, encoding="GB18030"))
        output = [self.capital_to_lower(doc) for doc in output]
        io.set_output('output_data', output)
        io.push_event('Out')
        # except Exception as e:
        #     print('warning oracle select failed', e)
        #     output = []


class SqldataDict(Action):
    '''数据库数据操作，对应列表元祖数据和对应长度列表，组成字典形式数据'''
    _id = '0dbea036-2d26-11ea-950b-f439090640bd'
    node_info = {
        "args": [
            ['sql_list', 'List', 'd7478836-2d27-11ea-be7b-f439090640bd'],
            ['key_list', 'List', 'd80ea8c6-2d27-11ea-a90b-f439090640bd'],
            ['In', 'Event', 'e76422a6-2d27-11ea-88ae-f439090640bd']],
        "returns": [
            ['dict_sql', 'Dict', 'eaee5ad4-2d27-11ea-9013-f439090640bd'],
            ['Out', 'Event', 'edde4ed8-2d27-11ea-b160-f439090640bd']]
    }

    def __call__(self, args, io):
        sql_list = args['sql_list']
        key_list = args['key_list']
        dict_sql = {}

        for dict_key, dict_value in zip(key_list, sql_list[0]):
            dict_sql[dict_key] = str(dict_value)

        io.set_output('dict_sql', dict_sql)
        io.push_event('Out')
