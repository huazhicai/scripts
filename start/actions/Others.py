# -*- coding: utf-8 -*-
"""
copyright. AIIT
created by LiQing.
created by LiQing
ccontact blacknepia@dingtail.com for more information
"""
import asyncio
from fake_useragent import UserAgent
from runtime.Action import Action

import time 
import requests
import gevent
import pymongo 
from copy import deepcopy 
import json 
from datetime import datetime 
import re 


class MergeFuTou(Action):
    _id = '1d3c5cc6-10f8-11ea-9e25-8cec452317f3'
    node_info = {"args": [
                          ['In', 'Event', 'dd02e53a-10f7-11ea-ae02-8cec4b4568f3']],
                 "returns": [
                             ['Out', 'Event', '09460f9c-10f8-11ea-bf71-8c123bd887f3']]}

    def __call__(self, args, io):
       
        futou_client = pymongo.MongoClient('localhost')
        futou_db = futou_client['futou']

        futou_col = futou_db['futou']
        yihui_col = futou_db['yihui']
        menzhen_col = futou_db['menzhen']

        merge_db = futou_client['hemodoalysis']
        merge_col = merge_db['BELLY_Dialysis']
       

        other_client = pymongo.MongoClient('192.168.66.57')
        other_db = other_client['futou']

        merge_db = other_client['hemodoalysis']
        merge_col = merge_db['BELLY_Dialysis']

        lis_col = other_db['lis']
        his_col = other_db['his']
        huayan_col = other_db['huayan']
        blbg_col = other_db['binglibaogao']
        szblbg_col = other_db['shenzhangbinglibaogao']
        yingxiangxue_col = other_db['yingxiangxue']

        for doc in futou_col.find({}, {'_id': 0}):
            patient_id = doc['patient_id'] 

            gerenbingshi = doc['gerenbingshi']
            if not gerenbingshi:
                continue 
            
            yihui_doc = yihui_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            menzhen_doc = menzhen_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
    
            lis_doc = lis_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            his_doc = his_col.find_one({'patient_id': patient_id}, {'_id': 0})
            if not his_doc:
                continue 
            
            zhuyuanxinxi, ruyuanjilu = MergeXueTou.handle_his(self, his_doc)
            for ryjl in ruyuanjilu:
                gerenbingshi_1 = deepcopy(gerenbingshi[0])
                for k, v in gerenbingshi_1.items():
                    if k == 'bingshi':
                        gerenbingshi_1[k] = ryjl[1]
                    elif k == 'riqi':
                        gerenbingshi_1[k] = ryjl[0]
                    elif isinstance(v, dict):
                        for i, j in v.items():
                            v[i] = ''
                    else:
                        gerenbingshi_1[k] = ''
                gerenbingshi.append(gerenbingshi_1)

            huayan_doc = huayan_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            blbg_doc = blbg_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            szblbg_doc = szblbg_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}

            lis_doc = lis_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            lis_new_doc = MergeXueTou().handle_shiyanshijianyan(lis_doc)

            yingxiangxue_doc = yingxiangxue_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            if yingxiangxue_doc:
                yingxiangxue_new_doc = yingxiangxue_doc['yingxiangxue']
                if yingxiangxue_new_doc:
                    yingxiangxue_data = yingxiangxue_new_doc[0]['yingxiangjiancha']
            else:
                yingxiangxue_data = {}

            
            doc['shengmingtizheng'] = yihui_doc.get('shengmingtizheng')
            # doc['yongyaojilu'] = menzhen_doc.get('yongyaojilu')
            doc['shiyanshijianyan'] = lis_new_doc
            doc['zhuyuanxinxi'] = zhuyuanxinxi
            doc['changqiyizhu'] = his_doc.get('changqiyizhu')
            doc['yingxiangyubaogao'] = {
                                        'yingxiangjiancha': yingxiangxue_data,
                                        'shenzangbinglibaogao': szblbg_doc.get('shenzangbinglibaogao'),
                                        'binglibaogao': blbg_doc.get('binglibaogao'),
                                        'xyssabbg': None,
                                        }
            # merge_col.insert_one(doc)
            merge_col.update_one({'patient_id': doc['patient_id']}, {'$set': doc}, upsert=True)
            time.sleep(1)
            # print(doc)
            


class MergeXueTou(Action):
    _id = '1d3c5cc6-10f8-11ea-9e25-8cec652317f3'
    node_info = {"args": [
                          ['In', 'Event', 'dd02e53a-10f7-11ea-ae02-8ce45365a8f3']],
                 "returns": [
                             ['Out', 'Event', '0952149c-10f8-11ea-bf71-8c123b42a2153']]}

    def __call__(self, args, io):
       
        other_client = pymongo.MongoClient('localhost')
        other_db = other_client['xuetou']

        yihui_col = other_db['yihui']
        menzhen_col = other_db['menzhen']


        merge_db = other_client['hemodoalysis']
        merge_col = merge_db['BLOOD_Dialysis']

        xuetou_client = pymongo.MongoClient('192.168.66.57')
        xuetou_db = xuetou_client['xuetou']

        xuetou_col = xuetou_db['xuetou']
        lis_col = xuetou_db['lis']
        his_col = xuetou_db['his']
        huayan_col = xuetou_db['huayan']
        blbg_col = xuetou_db['binglibaogao']
        szblbg_col = xuetou_db['shenzhangbinglibaogao']
        yingxiangxue_col = xuetou_db['yingxiangxue']
        
        for doc in xuetou_col.find({}, {'_id': 0}):
            patient_id = doc['patient_id'] 
            gerenbingshi = doc['gerenbingshi']
            if not gerenbingshi:
                continue
            
            yihui_doc = yihui_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            if yihui_doc:
               yihui_doc.pop('patient_id')

            # print(yihui_doc)
            menzhen_doc = menzhen_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}

            lis_doc = lis_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            lis_new_doc = self.handle_shiyanshijianyan(lis_doc)

            his_doc = his_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            if not his_doc:
                continue 
            
            zhuyuanxinxi, ruyuanjilu = self.handle_his(his_doc)
            for ryjl in ruyuanjilu:
                gerenbingshi_1 = deepcopy(gerenbingshi[0])
                for k, v in gerenbingshi_1.items():
                    if k == 'bingshi':
                        gerenbingshi_1[k] = ryjl[1]
                    elif k == 'riqi':
                        gerenbingshi_1[k] = ryjl[0]
                    elif isinstance(v, dict):
                        for i, j in v.items():
                            v[i] = ''
                    else:
                        gerenbingshi_1[k] = ''
                gerenbingshi.append(gerenbingshi_1)

            huayan_doc = huayan_col.find_one({'patient_id': patient_id}, {'_id': 0})
            if huayan_doc:
                huayan_new_doc = self.handle_huayan(huayan_doc['huayan'])
            else:
                huayan_new_doc = {}
          
            blbg_doc = blbg_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            szblbg_doc = szblbg_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}

            yingxiangxue_doc = yingxiangxue_col.find_one({'patient_id': patient_id}, {'_id': 0}) or {}
            if yingxiangxue_doc:
                yingxiangxue_new_doc = yingxiangxue_doc['yingxiangxue']
                if yingxiangxue_new_doc:
                    yingxiangxue_data = yingxiangxue_new_doc[0]['yingxiangjiancha']
            else:
                yingxiangxue_data = {} 


            doc['shengmingtizheng'] = yihui_doc['shengmingtizheng'] 
            # doc['yongyaojilu'] = menzhen_doc.get('yongyaojilu')
            doc['shiyanshijianyan'] = lis_new_doc
            doc['zhuyuanxinxi'] = zhuyuanxinxi
            doc['changqiyizhu'] = his_doc.get('changqiyizhu')
            
            doc['huayan'] = huayan_new_doc

            doc['yingxiangyubaogao'] = {
                                        'yingxiangjiancha': yingxiangxue_data,
                                        'shenzangbinglibaogao': szblbg_doc.get('shenzangbinglibaogao'),
                                        'binglibaogao': blbg_doc.get('binglibaogao'),
                                        'xyssabbg': None,
                                        }
            time.sleep(1)
            # merge_col.insert_one(doc)
            merge_col.update_one({'patient_id': doc['patient_id']}, {'$set': doc}, upsert=True)
            # print(doc['patient_id']) 
          

    def handle_huayan(self, doc):
        npcr = doc['npcr']
        urr = doc['urr']
        ztdbbhd = doc['ztdbbhd']
        ktv = doc['ktv']

        npcr_temp = []
        for item in npcr:
            new = {}
            new['jianchariqi'] = self.split_href(item['检查日期'])
            new['touxijianqishijian'] = item['透析间期时间']
            new['touxijianqiniaoliang'] = item['透析间期尿量']
            new['zhiliaohoutianshu'] = item['治疗后天数']
            new['npcr'] = item['nPCR']
            new['syctxhbun'] = item['上一次透析后BUN']
            new['tizhong'] = item['体重']
            new['touxijianqibun'] = item['透析间期BUN']
            new['xyctxqbun'] = item['下一次透析前BUN']
            new['txjqndbl'] = item['透析间期尿蛋白量']
            npcr_temp.append(new)

        urr_temp = []
        for item in urr:
            new = {}
            new['jianchariqi'] = self.split_href(item['检查日期'])
            new['touxihouniaosudan'] = item['透析后尿素氮']
            new['touxiqianjigan'] = item['透析前肌酐']
            new['touxihoujigan'] = item['透析后肌酐']
            new['touxiqianniaosu'] = item['透析前尿酸']
            new['zhiliaotianshu'] = item['治疗后天数']
            new['urr'] = item['URR']
            new['touxiqianniaosudan'] = item['透析前尿素氮']
            new['touxihouniaosu'] = item['透析后尿酸']
            urr_temp.append(new)

        ktv_temp = []
        for item in ktv:
            new = {}
            new['jianchariqi'] = self.split_href(item['检查日期'])

            new['touxiqianniaosu'] = item['透前尿素']
            new['zhiliaohoutianshu'] = item['治疗后天数']
            new['touxishijian'] = item['透析时间']
            new['touxihouniaosu'] = item['透后尿素']
            new['ktv'] = item['KT/V']
            new['tuoshuiliang'] = item['脱水量']
            new['tizhong'] = item['体重']
            ktv_temp.append(new)

        ztdbbhd_temp = []
        for item in ztdbbhd:
            new = {}
            new['jianchariqi'] = self.split_href(item['检查日期'])
            new['zhiliaohoutianshu'] = item['治疗后天数']
            new['zongtiejieheli'] = item['总铁结合力']
            new['xueqingtie'] = item['血清铁']
            new['xueqngtiedanbai'] = item['血清铁蛋白']
            new['ztdbbhd'] = item['转铁蛋白饱和度']
            new['yesuan'] = item['叶酸']
            new['vitb12'] = item['VitB12']
            new['zhuantiedanbai'] = item['转铁蛋白']

        out_put =  {
              'npcr': npcr_temp,
              'ktv': ktv_temp,
              'urr': urr_temp,
              'ztdbbhd': ztdbbhd_temp
        }

        return out_put

    def split_href(self, raw):
        ret = re.search(r'\d{4}-\d{1,2}-\d{1,2}', raw)
        if ret:
            return ret.group()

    def handle_shiyanshijianyan(self, doc):
        new_sysjy = []
        if doc:
            sysjy = doc['shiyanshijianyan']
            if sysjy:
                for item in sysjy[0]:
                    result = self.recursion(item)
                    new_sysjy.append(result)
        return new_sysjy

    def recursion(self, doc):
        if isinstance(doc, dict):
            new_doc = self.capital_to_lower(doc)
            for k, v in new_doc.items():
                new_doc[k] = self.recursion(v)     
        elif isinstance(doc, list):
            new_doc = []
            for i in doc:
                temp = self.recursion(i)
                new_doc.append(temp)
        else:
            new_doc = doc 

        return new_doc

    def capital_to_lower(self, doc):
        new = {}
        for key, value in doc.items():
           new[key.lower()] = value
        return new 

    def handle_his(self, doc):
        zhuyuanxinxi = doc['zhuyuanxinxi'] or []
        ruyuanjilu = []
        for i in zhuyuanxinxi:  
            binganshouye = i['binganshouye'] if zhuyuanxinxi else None 
            ryjl = binganshouye.pop('ruyuanjilu')
            ruyuanshijian = binganshouye['ruyuanshijian']
            if ruyuanshijian:
                nian = re.sub(r'年|月', '-', ruyuanshijian)
                ri = re.sub(r'日', ' ', nian)
                shi = re.sub(r'时|分', ":", ri)

                shijian = shi +"00"
                rysj = datetime.strptime(shijian, '%Y-%m-%d %H:%M:%S')
            else:
                rysj = None 
            ruyuanjilu.append((rysj, ryjl))
        return zhuyuanxinxi, ruyuanjilu

