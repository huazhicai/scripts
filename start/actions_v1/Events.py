# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by liqing.
contact blacknepia@dingtail.com for more information
"""

from runtime.Action import Action
import decimal
from datetime import datetime
import copy
import pymongo
from functools import reduce


class Start(Action):
    _id = '9ed37096-bc78-47c9-b0d0-44fef1f8002d'
    node_info = {"args": [['Default', 'Event', 'be723dbe-0053-11ea-8738-8cec43253f9f']],
                 "returns": [['Out', 'Event', 'a9f4fe1f-00b9-413c-a332-f98325127465']]}

    def __call__(self, args, io):
        io.push_event('Out')


class PatientIdArray(Action):
    _id = '9e6325af-bc78-47c9-b0d0-44fef1f8002d'
    node_info = {"args": [['In', 'Event', 'be723dbe-1254-11ea-8738-8cec4bd83f9f']],
                 "returns": [['futou_id', 'List', 'be723dbe-0053-11ea-3258-8cec4bd83f9f'],
                             ['xuetou_id', 'List', 'b6524abe-0053-11ea-8738-8cec4bd83f9f'],
                             ['Out', 'Event', 'a9f4fe1f-00b9-413c-a332-3254f6327465']]}

    def __call__(self, args, io):
        futou_id = [45, 2534, 1344, 1641, 926, 1400, 1685, 1341, 2936, 1141, 1539, 295, 231, 1887,
                    942, 2317, 793, 1567, 1760, 1184, 2256, 1655, 2347, 1898, 1913, 1430, 2190,
                    2339, 2164, 1106, 1711, 609, 2045, 2099, 206, 1710, 1145, 1884, 2144, 2013,
                    208, 257, 1701, 1745, 982, 1937, 1355, 494, 1528, 2330, 2090, 717, 27, 931,
                    1405, 732, 1716, 2253, 111, 2286, 2331, 2524, 1608, 2175, 374, 2058, 550, 237,
                    52, 1087, 803, 2704, 1462, 1056, 1059, 1851, 949, 1623, 1609, 1214, 2916, 791,
                    966, 503, 2093, 1133, 1157, 1789, 121, 421, 1508, 2222, 2000, 499, 1790, 1487,
                    512, 2183, 2097, 1743, 1909, 217, 580, 1997, 116, 590, 1283, 1366, 2081, 326,
                    1199, 2453, 1097, 1104, 1517, 2677, 2042, 1736, 2128, 1174, 1409, 940, 1308,
                    2311, 514, 1767, 1048, 1735, 1177, 2018, 634, 1372]
        futou_50 = [45, 2534, 1344, 1641, 926, 1400, 1685, 1341, 2936, 1141, 1539, 295, 231, 1887,
                    942, 2317, 793, 1567, 1760, 1184, 2256, 1655, 2347, 1898, 1913, 1430, 2190,
                    2339, 2164, 1106, 1711, 609, 2045, 2099, 206, 1710, 1145, 1884, 2144, 2013,
                    208, 257, 1701, 1745, 982, 1937, 1355, 494, 1528, 2330]

        # [2286, 332]

        xuetou_id = [16497, 16351, 12933, 18816, 6629, 2432, 5670, 5521, 9567, 3058, 14865, 19889,
                     8641, 14140, 7328, 17338, 22690, 18695, 21656, 8454, 13494, 7370, 3433, 17622,
                     9766, 4564, 20332, 14278, 19989, 6555, 16226, 6188, 16379, 8625, 2603, 7558,
                     15739, 19608, 22427, 16350, 371, 22530, 20614, 17638, 6003, 7426, 21412, 18252,
                     139, 2484, 4896, 232, 11538, 18769, 6322, 20902, 4348, 13220, 5505, 20084, 15015,
                     4377, 3893, 17402, 6041, 11713, 18783, 11205, 10953, 5822, 12778, 186, 13621, 5287,
                     21983, 16411, 13764, 3050, 23587, 5464, 4699, 13185, 12557, 8760, 2062, 14442, 21901,
                     2718, 16389, 10717, 8387, 1540, 3902, 6515, 22326, 5615, 9221, 2549, 2850, 11070,
                     14202, 7774, 22684, 3740, 7902, 12721, 8225, 11396, 10481, 19845, 4905, 16935, 2280,
                     13905, 1622, 14104, 10194, 23166, 12987, 6805, 18272, 18418, 23651, 5630, 19275, 9709,
                     18030, 6806, 2592, 13511, 7786, 12193, 7916, 674, 22155, 6239, 3285, 16943, 20789, 15013,
                     17034, 21921, 17744, 6762, 7687, 10322, 13423, 11506, 16881, 15825, 22676, 19918, 17461,
                     13806, 21572, 21586, 10035, 19233, 9996, 20848, 7025, 6345, 22291, 15500, 5468, 11191,
                     8990, 6691, 21519, 2891, 18780, 14126, 7855, 12108, 16909, 23272, 14000, 12324, 18808,
                     5117, 15812, 13969, 7512, 2327, 22386, 8325, 20226, 20006, 21217, 12484, 2323, 16783, 12713,
                     2006, 506, 13619, 1828, 15065, 11932, 8715, 7594, 7021]
        xuetou_50 = [13969, 16351, 12933, 18816, 6629, 2432, 5670, 5521, 9567, 3058, 14865, 19889,
                     8641, 14140, 7328, 17338, 22690, 18695, 21656, 8454, 13494, 7370, 3433, 17622,
                     9766, 4564, 20332, 14278, 19989, 6555, 16226, 6188, 16379, 8625, 2603, 7558,
                     15739, 19608, 22427, 16350, 371, 22530, 20614, 17638, 6003, 7426, 21412, 18252,
                     139, 2484]
        # [10717, 16389, 8641, 19889]

        io.set_output('futou_id', futou_id)
        io.set_output('xuetou_id', xuetou_id)
        io.push_event('Out')


# self.collection.update({'patient_id': one_data['patient_id']}, {'$set': one_data}, upsert=True)
# print(one_data)

class MergeData(Action):
    _id = 'dc32ecb6-e967-11e9-9dab-8cec4b321af3'
    node_info = {"args": [['source_data', 'Dict', 'ce693d53-f3a7-11e9-9801-8cec4985af3'],
                          ['add_data', 'List', 'ce693d54-f3a7-2345-a29c-8cec4bd887f3'],
                          ['destination', 'String', 'c6532ac5-f3a7-11e9-bf99-8cec4bd887f3'],
                          ['overwrite', 'String', 'c6532ac5-f3a7-11e9-bf99-8cec4521a7f3'],
                          ['In', 'Event', 'ce693d56-f3a7-11e9-a80a-63acepa887f3']],

                 "returns": [['doc', 'Dict', '2865231a-4f47-498b-873e-993df96884ba'],
                             ['Out', 'Event', 'ce693d58-f3a7-11e9-bb19-8cec653ac7f3']
                             ]}

    def over_write(self, ov_key, source, data):
        obj_doc = source[ov_key]
        for key, val in data.items():
            if key in list(obj_doc.keys()):
                if isinstance(obj_doc[key], str):
                    if isinstance(val, str) and len(obj_doc[key].strip()) < len(val.strip()):
                        obj_doc[key] = val
                else:
                    pass
            elif isinstance(val, dict):
                self.over_write(ov_key, source, val)
            elif isinstance(val, list):
                for i in val:
                    self.over_write(ov_key, source, i)
                    break

    def format_data(self, doc1, doc2):
        for key, val in doc1.items():
            if key in list(doc2.keys()):
                doc1[key] = doc2[key]
            elif isinstance(val, dict):
                self.format_data(val, doc2)
        # print(doc1)
        return doc1

    def put_val(self, dest, source, data):
        for key, val in source.items():
            if key == dest:
                if isinstance(val, list):
                    val.append(data)
                elif isinstance(val, dict):
                    self.recursion(val, data)
            elif isinstance(val, list):
                _ = [self.put_val(dest, i, data) for i in val if i]
            elif isinstance(val, dict):
                self.put_val(dest, val, data)

    def recursion(self, doc1, doc2):
        for key, val in doc1.items():
            if isinstance(val, dict):
                self.recursion(val, doc2)
            elif isinstance(val, list):
                if doc2.get(key):
                    doc1[key].extend(doc2[key])
            else:
                val = doc2.get(key, None)
                if val:
                    if isinstance(val, datetime):
                        val = val.strftime('%Y-%m-%d')
                    if isinstance(val, decimal.Decimal):
                        val = float(val)
                    doc1[key] = val
        return doc1

    def __call__(self, args, io):
        source_data = args['source_data']
        # source_data = {"yibanziliao": {"yibaohao": "", "jiuzhenkahao": "", "binglihao": "", "xingming": "", "xingbie": "", "shenfenzhenghao": "", "chushengriqi": None, "minzu": "", "hunyinzhuangkuang": "", "shengao": "", "tizhong": "", "xiyan": "", "yinjiu": "", "shilizhangai": "", "yiliaofufeifangshi": "", "shoucitouxishijian": None, "jieshouriqi": None, "sheng": "", "shi": "", "quxian": "", "gongzuodanwei": "", "zhiye": "", "dizhi": "", "lianxidianhua1": "", "lianxidianhua2": "", "wenhuachengdu": "", "zongjiaoxinyang": "", "pingjinghezuo": "", "duijibingrenshi": "", "sfjsgyhjhjkzd": "", "ywylyyxd": "", "juzhuzhuangkuang": "", "zhaoliaozhe": ""}, "zhuyuanxinxi": [{"binganshouye": {"xingming": "", "xingbie": "", "chushengriqi": None, "nianling": "", "guoji": "", "chushengdi": "", "jiguan": "", "minzu": "", "shenfenzhenghao": "", "ylbxzffs": "", "yiliaofufeifangshi": "", "zhiye": "", "hunyin": "", "xianzhuzhi": "", "dianhua": "", "gzdwjdz": "", "lianxirenxingming": "", "guanxi": "", "lianxirendizhi": "", "lianxirendianhua": "", "ruyuantujing": "", "ruyuanshijian": "", "ruyuanzhenduan": "", "chuyuanshijian": "", "shijizhuyuantianshu": "", "churuyuanjilu": [{"zhenduanleixing": "", "chuyuanzhenduan": "", "jibingbianma": "", "ruyuanbingqing": ""}], "sszddwbys": "", "binglizhenduan": "", "binglihao": "", "xuexing": "", "hbsag": "", "hcvab": "", "hivab": "", "meidukangti": "", "chuanranbingbaogao": "", "rh": "", "yaowuguomin": "", "ssjczjl": [{"ssjczbm": "", "ssjczrq": None, "ssjczmc": "", "mazuifangshi": "", "qiekouyuhedengji": ""}], "liyuanfangshi": "", "sfycy31tnzzyjh": "", "lnsshzhmsj": ""}, "zhuyuanfeiyong": {"zhuyuanfeiyongzongji": "", "ybylfwf": "", "hulifei": "", "xiyao": "", "zhongchengyao": "", "zhongcaoyao": "", "yingxiangxuezhenduanfei": "", "shiyanshizhenduanfei": "", "baidanbaizhipinfei": "", "xuefei": "", "shoushufei": "", "qiudanbaizhipinfei": "", "zhenduanfei": "", "mazuifei": "", "nxyzzpf": "", "xbyzzpf": "", "zhenliaofei": "", "jcyycxyyclf": "", "zlyycxyyclf": "", "ssyycxyyclf": "", "qita": ""}}], "gerenbingshi": [{"riqi": None, "tijian": {"yingyangzhuangtai": "", "tiwei": "", "fuzhong": "", "fuzhongchengdu": "", "zhuankejiancha": ""}, "bingshi": {"shenyizhishi": "", "pdshi": "", "zhusu": "", "xianbingshi": "", "jiwangshi": "", "gerenshi": "", "hunyushi": "", "jiazushi": "", "guominyaowu": ""}}], "changqiyizhu": [{"kaishishijian": "", "yizhuneirong": "", "tingzhishijian": ""}], "xueguantonglu": [{"jianlishijian": None, "tongluleixing": "", "tonglujianlibuwei": "", "daoguanleixing": "", "chuancifangshi": "", "tingyongshijian": None, "tingyongyuanyin": ""}], "touxifangan": {"lishijilu": [{"jianlishijian": None, "gansuleixing": "", "gantizhong": "", "touxipinglv": "", "touxileixing": "", "touxiqileixing": "", "touxishichang": "", "zhihuanyezongliang": ""}], "crrtjilu": [{"riqi": None, "jiqi": "", "zhongkongguan": "", "shijian": ""}], "hpjilu": [{"riqi": None, "jiqi": "", "zhongkongguan": "", "shijian": ""}], "tpejilu": [{"riqi": None, "jiqi": "", "zhongkongguan": "", "shijian": ""}], "dfppjilu": [{"riqi": None, "jiqi": "", "zhongkongguan": "", "shijian": ""}], "iajilu": [{"riqi": None, "jiqi": "", "None": "", "shijian": ""}]}, "touxijilu": [{"zhiliaoriqi": None, "zhiliaoleixing": "", "touxiqianjingtizhong": "", "touxihoujingtizhong": "", "bmi": "", "touqianshousuoya": "", "touqianshuzhangya": "", "touqianxinlv": "", "touqianhuxi": "", "cexueyabuwei": "", "shijitouxishijian": "", "shijituoshui": "", "tongluxueliuqingkuang": "", "zongzhihuanyeliang": "", "shihengzonghezheng": "", "ixingmofanying": "", "iixingmofanying": "", "xinlvshichang": "", "touhoushousuoya": "", "touhoushuzhangya": "", "touhouxinlv": "", "touhouhuxi": "", "chixuxingdixueya": "", "touxizhongdixueya": "", "touxiqiangaoxueya": "", "touxizhonggaoxueya": "", "touxihougaoxueya": ""}], "zhuanguijilu": [{"zhuanguiriqi": None, "zhuanguifenlei": "", "zhuanguileixing": ""}], "zhenduanjilu": [{"zhenduanriqi": None, "zhenduanmingcheng": "", "shuxingleibie": "", "shujulaiyuan": ""}], "shoushujilu": [{"shoushushijian": None, "shoushuyuanyin": "", "shoushuleixing": ""}], "yongyaojilu": {"changqikoufuyongyao": [{"kaiyaoshijian": None, "yaowumingcheng": "", "guige": "", "yicijiliang": "", "danwei": "", "yongfa": "", "yongyaopinlv": "", "tingzhishijian": None, "shujulaiyuan": ""}], "changqizhenjiyongyao": [{"kaiyaoshijian": None, "yaowumingcheng": "", "guige": "", "yicijiliang": "", "danwei": "", "yongfa": "", "yongyaopinlv": "", "tingzhishijian": None, "shujulaiyuan": ""}]}, "shengmingtizheng": {"p": [{"shijian": "", "shuzhi": ""}], "t": [{"shijian": "", "shuzhi": ""}], "r": [{"shijian": "", "shuzhi": ""}], "bp": [{"shijian": "", "shuzhi": ""}], "shengao": [{"shijian": "", "shuzhi": ""}], "tizhong": [{"shijian": "", "shuzhi": ""}], "niaoliang": [{"shijian": "", "shuzhi": ""}], "chuliang": [{"shijian": "", "shuzhi": ""}], "ruliang": [{"shijian": "", "shuzhi": ""}], "xuetang": [{"shijian": "", "shuzhi": ""}]}, "huayan": {"ktv": [{"jianchariqi": None, "zhiliaohoutianshu": "", "ktv": "", "touxiqianniaosu": "", "touxihouniaosu": "", "touxishijian": "", "tuoshuiliang": "", "tizhong": ""}], "urr": [{"jianchariqi": None, "zhiliaotianshu": "", "urr": "", "touxiqianjigan": "", "touxihoujigan": "", "touxiqianniaosudan": "", "touxihouniaosudan": "", "touxiqianniaosu": "", "touxihouniaosu": ""}], "npcr": [{"jianchariqi": None, "zhiliaohoutianshu": "", "npcr": "", "syctxhbun": "", "xyctxqbun": "", "touxijianqibun": "", "touxijianqishijian": "", "touxijianqiniaoliang": "", "txjqndbl": "", "tizhong": ""}], "ztdbbhd": [{"jianchariqi": None, "zhiliaohoutianshu": "", "ztdbbhd": "", "xueqingtie": "", "xueqingtiedanbai": "", "zongtiejieheli": ""}]}, "shiyanshijianyan": [{"jianyanshijian": "", "jianyanmudi": "", "yangbenhao": "", "jianyanxiangqing": {"jianyanmudi": "", "jianyanjieguo": [{"jianyanxiangmu": "", "danwei": "", "ceshijieguo": "", "cankaodixian": "", "cankaogaoxian": "", "shenheshijian": ""}]}}], "yingxiangyubaogao": {"yingxiangjiancha": [{"jianchariqi": None, "jianchaleixing": "", "jianchaxiangmu": "", "yingxiangbiaoxian": "", "zhenduanjielun": ""}], "shenzangbinglibaogao": [{"baogaoriqi": None, "guangxuexianweijing": "", "shenxiaoqiu": "", "shenxiaoguan": "", "shenxueguan": "", "shenjianzhi": "", "tsrsmyzh": "", "binglizhenduan": "", "zongjie": ""}], "binglibaogao": [{"baogaoriqi": None, "binglizhenduan": "", "bingdongbaogao": "", "buchongbaogao": ""}], "xysszbbg": [{"baogaoshijian": None, "baogaomingchen": "", "baogaotupian": ""}]}, "pingguxiangmu": {"yyzplbsds": [{"tianxieshijian": None, "fenshu": "", "jielun": ""}], "jlzplbsas": [{"tianxieshijian": None, "fenshu": "", "jielun": ""}], "askrgcrwjepq": [{"tianxieshijian": None, "zongfen": "", "eliangfenshu": "", "nliangfenshu": "", "pliangfenshu": "", "lliangfenshu": ""}], "xzzzplbscl9""": [{"tianxieshijian": None, "zongfen": "", "zongjunfen": "", "qutihuayinzifen": "", "qpzzyzf": "", "rjgxmgyzf": "", "yiyuyinzifen": "", "jiaolvyinzifen": "", "diduiyinzifen": "", "kongbuyinzifen": "", "pianzhiyinzifen": "", "jingshenbingxing": "", "qitayinzifen": "", "yangxingxiangmushu": "", "yinxingxiangmushu": "", "yangxingzhengzhuangjunfen": ""}], "lwshzclb": [{"tianxieshijian": None, "shehuizhichizongfen": "", "jtnzcfs": "", "jtwzcfs": ""}], "zgzhxyyzkpgsga": [{"tianxieshijian": None, "sgapingfen": "", "jinshibianhua": "", "jinshishijian": "", "jsgbdlx": "", "weichangdaozhengzhuang": [], "zongdeyichang": "", "guoqu2zhougaibian": "", "pixiazhifangjianshao": "", "jirouweisuo": "", "shuizhong": "", "wolizuo": "", "woliyou": ""}], "shzlwjkdqolsftm": [{"tianxieshijian": None, "zongfen": "", "zhengzhuangyingxiangpingfen": "", "shenbingyingxiangpingfen": "", "shenbingfudanpingfen": "", "gongzuozhuangtaipingfen": "", "renzhigongnengpingfen": "", "shehuiyingxiangpingfen": "", "xinggongnengpingfen": "", "shuimianzhiliangpingfen": "", "shzclpf": "", "yhryzcdpf": "", "ziwojiankangpingfen": "", "hzmydpf": "", "shentigongnengpingfen": "", "shehuijuesepingfen": "", "tengtongdupingfen": "", "zongtizhuangkuangpingfen": "", "qingganzhuangkuangpingfen": "", "shehuiqingganpingfen": "", "shehuigongnengpingfen": "", "jinglitilipingfen": ""}], "pxzfcdpg": [{"tianxieshijian": None, "shangbiwei": "", "shangbijiwei": "", "etjpzhd": "", "stjpzhd": "", "qgspzhd": "", "jjxpzhd": ""}], "shengwuzukangpinggu": [{"tianxieshijian": None, "swzkcdsjd": "", "stzqztzswdzk": "", "ecwtbw": "", "tizhifang": ""}], "wlzypg": [{"tianxieshijian": None, "wolizuo": "", "woliyou": ""}], "quanshenqingkuangpinggu": [{"tianxieshijian": None, "yingyangzhuangkuang": "", "xinxueguangongneng": "", "manxingyanzheng": "", "gailindaixie": "", "waikeqingkuang": "", "touxichongfenxing": ""}]}, "siwangjilu": {"siwangriqi": None, "shijian": "", "siwangzhuyaoyuanyin": "", "swcyyy1": "", "swcyyy2": "", "swcyyy3": "", "sqstdfs": "", "siqianzhongzhitidai": "", "siqianzhitiyuanyin": "", "jieshouguoshenyizhi": "", "zhycyzrq": None}}
        add_data = args['add_data']
        # print(add_data)
        destination = args['destination']
        overwrite = args['overwrite']

        flag = True
        for item in add_data:
            if item:
                if destination in ['gerenbingshi']:
                    schema = copy.deepcopy(source_data[destination][0])
                    item = self.format_data(schema, item)
                self.put_val(destination, source_data, item)
            if overwrite and flag:
                self.over_write(overwrite, source_data, item)
                flag = False

                # print(source_data)
        io.set_output('doc', source_data)
        io.push_event('Out')


class FilterData(Action):
    _id = 'dc32ecb6-e967-11e9-9dab-8ce654a21af3'
    node_info = {"args": [
        ['refer_keys', 'List', 'ce663ac4-f3a7-2345-a29c-8cec4bd887f3'],
        ['refer_data', 'Dict', 'c6532015-f3a7-3201-bf99-8cec4bd887f3'],
        ['obj_keys', 'List', 'ce32ac53-f3a7-11e9-9801-8cec4985af3'],
        ['input_array', 'List', 'c6532015-f3a7-3201-bf99-8cec632587f3'],
        ['In', 'Event', 'ce693d56-f3a7-11e9-a80a-862acpa887f3']],
        "returns": [['output_array', 'List', '2632511a-4f47-498b-1234-993df96884ba'],
                    ['Out', 'Event', 'ce693d58-f3a7-11e9-3251-8cec653ac7f3']]}

    def get_val(self, label, doc):
        if doc and doc.get(label):
            return doc[label]
        elif doc:
            for key, val in doc.items():
                if isinstance(val, dict):
                    if self.get_val(label, val):
                        return self.get_val(label, val)
                elif isinstance(val, list):
                    for i in val:
                        if self.get_val(label, i):
                            return self.get_val(label, i)

    def __call__(self, args, io):
        refer_keys = args['refer_keys']  # [10114, 10103, 10102, 10104, 10106]
        data = args['refer_data']
        obj_keys = args['obj_keys']
        input_array = args['input_array']

        assert len(refer_keys) == len(obj_keys)

        shenfenzhenghao = data[refer_keys[0]]
        binglihao = data[refer_keys[1]]
        jiuzhenkahao = data[refer_keys[2]]
        xingming = data[refer_keys[3]]
        chushengriqi = data[refer_keys[4]]

        print(len(input_array))
        temp = []
        for item in input_array:

            sfz = self.get_val(obj_keys[0], item)
            if shenfenzhenghao and sfz:
                if shenfenzhenghao == sfz:
                    temp.append(item)
                continue

            blh = self.get_val(obj_keys[1], item)
            if binglihao and blh:
                if binglihao == blh:
                    temp.append(item)
                continue

            jzkh = self.get_val(obj_keys[2], item)
            if jiuzhenkahao and jzkh:
                if jiuzhenkahao == jzkh:
                    temp.append(item)
                continue

            if not (shenfenzhenghao or binglihao or jiuzhenkahao):
                xingm = self.get_val(obj_keys[3], item)
                chshrq = self.get_val(obj_keys[4], item)
                if xingming == xingm and chushengriqi.strip()[:10] == chshrq.strip()[:10]:
                    temp.append(item)
        print(len(temp))
        io.set_output('output_array', temp)
        io.push_event('Out')


class QuChong(Action):
    _id = 'dc32ecb6-e967-11e9-9dab-985213621af3'
    node_info = {"args": [['refer_key', 'Int', '65214583-f3a7-11e9-9801-8cec4985af3'],
                          ['input_array', 'List', 'c5214587-f3a7-2345-a29c-8cec4bd887f3'],
                          ['In', 'Event', 'ce693d56-f3a7-11e9-a80a-8685aae887f3']],
                 "returns": [['output_array', 'List', '2632511a-4f47-498b-873e-993df96884ba'],
                             ['Out', 'Event', 'ce652148-f3a7-11e9-3251-8cec653ac7f3']]}

    def quchong(self, key, array):
        seen = set()
        new_array = []
        for a in array:
            temp = a[key]
            if temp not in seen:
                seen.add(temp)
                new_array.append(a)
        return new_array

    def __call__(self, args, io):
        refer_key = args['refer_key']
        data = args['input_array']

        out_data = self.quchong(refer_key, data)

        io.set_output('output_array', out_data)
        io.push_event('Out')


class FusionDuplicate(Action):
    """获取mongodb中身份证重复的数据，如果身份证不存在就根据重复的病历号
      合并重复的数据，重新保存到数据库，删除原来的重复数据"""
    _id = 'dc32ecb6-e967-11e9-9dab-986325ac1af3'
    node_info = {"args": [['sfzh_blh_jzkh', 'List', '65123883-f3a7-11e9-9801-8ce23155af3'],
                          ['collection', 'Any', '65214583-f3a7-11e9-9801-8ce23155af3'],
                          ['In', 'Event', 'ce693d56-f3a7-11e9-a80a-8681235887f3']],
                 "returns": [['new_doc', 'Dict', '26adfa1a-4f47-498b-873e-993df96884ba'],
                             ['Out', 'Event', '14785218-f3a7-11e9-3251-8cec653ac7f3']]}

    def quchong(self, array):
        seen = set()
        new_array = []
        for a in array:
            if len(a) == len(list(filter(lambda x: isinstance(x, dict), a.values()))):
                b = []
                for val in a.values():
                    b.extend(list(filter(lambda x: not (isinstance(x, list) \
                                                        or isinstance(x, dict)), val.values())))
            else:
                b = list(filter(lambda x: not (isinstance(x, list) or isinstance(x, dict)), a.values()))
            temp = tuple(b)
            if temp not in seen:
                seen.add(temp)
                new_array.append(a)
        return new_array

    def combine(self, doc1, doc2):
        for key, val in doc1.items():
            if isinstance(val, dict):
                self.combine(doc1[key], doc2[key])
            elif isinstance(val, list):
                val.extend(doc2[key])
                doc1[key] = self.quchong(val)
            else:
                if not val:
                    doc1[key] = doc2[key]
                elif doc2[key] and len(str(val)) < len(str(doc2[key])):
                    doc1[key] = doc2[key]
        return doc1

    def __call__(self, args, io):
        # mongo_url = args['host'] or 'localhost'
        # mongo_db = args['db'] or 'hemodialysis'
        # mongo_chart = args['collection'] or 'BLOOD_Dialysis'
        # client = pymongo.MongoClient(mongo_url)
        # db = client[mongo_db]
        collection = args['collection']
        # data = args['data']
        sfzh_blh_jzkh = args['sfzh_blh_jzkh']
        sfzh_blh_jzkh = ('shenfenzhenghao', 'binglihao', 'jiuzhenkahao')
        for i in sfzh_blh_jzkh:
            key = "yibanziliao.{}".format(i)

            result = collection.aggregate([
                {"$match": {key: {"$ne": '', "$exists": 1}}},
                {"$group": {"_id": '$' + key, "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}},
                {"$sort": {"modify_time": 1}}
            ])
            objs_s = [i['_id'] for i in result]

            for item in objs_s:
                result = list(collection.find({key: item}, {'_id': 0}).sort({"yibanziliao.modify_time": -1}))
                new_doc = reduce(self.combine, result)
                print(i, item)
                collection.delete_many({key: item})
                # self.collection.insert_one(new_doc)
                io.set_output('new_doc', new_doc)
                io.push_event('Out')

        # io.set_output('out_data', data)


class GetModifyTime(Action):
    _id = 'dc32ecb6-e967-11e9-9dab-9863265c1af3'
    node_info = {"args": [
        ['collection', 'Any', '65214583-f3a7-11e9-9801-83260145af3'],
        ['In', 'Event', 'ce693d56-1234-11e9-a80a-8681235887f3']],
        "returns": [['sql', 'String', '26adfa1a-4f47-498b-873e-993df321456a'],
                    ['Out', 'Event', '14732118-f3a7-11e9-3251-8cec653ac7f3']]}

    def __call__(self, args, io):
        collection = args['collection']
        modify_time = collection.find({}, {"yibanziliao": {"modify_time": 1}}).sort({"yibanziliao": \
                                                                                         {"modify_time": -1}}).limit(1)
        modify_time = datetime.strptime(list(modify_time)[0], '%Y-%m-%d %H:%M:%S')

        sql = 'select id from patinet where modify_time>Convert(datetime, {})'.format(modify_time)

        io.set_output('sql', sql)
        io.push_event('Out')
