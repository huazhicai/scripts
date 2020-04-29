# coding:utf-8

version = 'error'
buildDate = '2015-02-23 11:30:00'

try:
    import pysvn
except:
    pysvn = None

if pysvn:
    svn_client = pysvn.Client()
    try:
        version = '%d' % svn_client.info2('.'.decode('gb2312').encode('utf-8'))[0][1]['last_changed_rev'].number
    except pysvn.ClientError:
        pass
