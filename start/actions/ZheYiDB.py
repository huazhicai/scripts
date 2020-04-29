# -*- coding: utf-8 -*-
from runtime.Action import Action
import decimal
from datetime import datetime
from actions.data_structure.singleton_structure_content import new_content, set_config_path


class FuTouData(Action):
    _id = '507c4cde-10f4-23ea-b977-10231254878f3'
    node_info = {"args": [['patient_id', 'Int', '518543v8-10f4-52ea-b2af-8ce8523147f3'],
                          ['connect', 'Any', '50df5792-3244-11ea-a522-8cec7hac67f3'],
                          ['In', 'Event', '6e02c34c-12f4-11ea-93d0-7ujjakb917f3']],
                 "returns": [['ybzl', 'Dict', '518543v8-10f4-6523-b2af-8cec4bd347f3'],
                             ['content', 'Any', 'j5624587a8-10f4-5aez-b2af-8cec4bd347f3'],
                             ['Out', 'Event', '6ec41528-50f4-11ea-90cf-8clack21f7f3']
                             ]}

    def convert_data(self, array, key):
        for doc in array:
            if doc[key] == True:
                doc[key] = 1
            elif doc[key] == False:
                doc[key] = 2

    def split_yongyaojilu(self, arry):
        koufu = []
        zhenji = []
        # ['kaiyaoshijian', 'yaowumingcheng', 'guige', 'yongyaopinlv',
        #  'yicijiliang', 'danwei', 'yongfa', 'tingzhishijian']
        for item in arry:
            if item:
                if item.get('yongfa') and '口' in item['yongfa']:
                    koufu.append({
                        21401: item['kaiyaoshijian'],
                        21402: item['yaowumingcheng'],
                        21403: item['yicijiliang'],
                        21404: item['yongyaopinlv'],
                        21405: item['yongfa'],
                        21406: item['tingzhishijian'],
                        21407: 1,  # 数据来源
                        21408: item['danwei'],
                    })
                # elif item.get('guige') and ('针' in item.get('guige') or '注' in item.get('guige')):
                else:
                    zhenji.append({
                        21501: item['kaiyaoshijian'],
                        21502: item['yaowumingcheng'],
                        21503: item['yicijiliang'],
                        21504: item['yongyaopinlv'],
                        21505: item['yongfa'],
                        21506: item['tingzhishijian'],
                        21507: 1,  # 数据来源
                        21508: item['danwei'],
                    })
        return koufu, zhenji

    def get_data(self, sql, keys):
        out_data = []
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        while row:
            row_data = dict(zip(keys, row))
            for key, val in row_data.items():
                if val in ['-9999.0', '-9999']:
                    val = None
                if isinstance(val, decimal.Decimal):
                    val = float(val)
                elif isinstance(val, datetime):
                    val = val.strftime('%Y-%m-%d %H:%M:%S')
                row_data[key] = val

            out_data.append(row_data)
            row = self.cursor.fetchone()
        return out_data

    def __call__(self, args, io):
        patient_id = args['patient_id']
        connect = args['connect']
        self.cursor = connect.cursor()

        ybzl_sql = '''
            select MedicareID, SeeDoctorID, InhospitalID, PatientName, Sex, IdentityCardID,
            BirthdayTime, Nationality, Marriage, DialysisFrontStature, DialysisFrontAvoirdupois,
            PaymentType,  FirstPDTime, SeeDoctor_time, Origin, shi, quxian, Workunits, Profession,
            HouseAddress, PatientPhone, PatientPhone2, EducationGrade, Faith, Favourer, create_time
            from patientInfo where Patientid={}'''.format(patient_id)
        ybzl_keys = [20101, 20102, 20103, 20104, 20105, 20114, 20106, 20107, 20108, 20109, 20110, 20115,
                     20116, 20117, 20118, 20119, 20120, 20121, 20122, 20123,
                     20124, 20125, 20126, 20127, 20133, 'modify_time']

        bingshi_sql = '''select SFRIQI, JYBINGSHI, MQZS, GXYA, XZBING, XueTouS, NXGUANBING, TNBING, ShenYiZS, ShuXueS,
                      WZXUEGUANBINGBIAN, GBING, YMSHI, TSAIHAO, HunYuS, JiaZuS, Brbsqt, XUEYA, MBO, FaYu, TWEN as tiwen,
                      HXI, YingYang from BRBS where Patientid={}'''.format(patient_id)
        bingshi_keys = [20201, 20212, 20222, 20214, 20224, 20225, 20217, 20215, 20227, 20228, 20218,
                        20229, 20221, 20230, 20231, 20232, 20220, 20301, 20302, 20303, 20304, 20305, 20202]

        jbqk_sql = '''select SFRIQI, SFFangShi, TZHONG, XYA, FuZhong, NLIANG, ChaoLvL, maibo
                            from YBQK where patientid={}'''.format(patient_id)
        jbqk_keys = [20501, 20502, 20503, 20504, 20506, 20507, 20508, 20505]

        zhenduan_sql = 'select ZDRIQI, ZD, ZYJLType from ZDUAN where patientid={}'.format(patient_id)

        zhenduan_keys = [21101, 21102, 21103]

        txfa_sql = '''select FARIQI, TXFANGSHI, TXY1, TXYND1, GNDJL1,  GND1, CFSJ1 
                from TXFA where patientid={}'''.format(patient_id)
        txfa_keys = [20601, 20602, 20603, 20604, 20605, 20606, 20607]

        txchfxpg_sql = '''select PGDate, FTHTS, BZTZ, TZ, TNZSL, FMKTV, CSKTV, ZKTV, FMCCR, SCCCR, ZCCT,
                            NPNA, NLSRL, LBMCK from TXCFXPG where patientid={}'''.format(patient_id)

        txchfxpg_keys = [21207, 21208, 21209, 21210, 21211, 21202, 21201,
                         21203, 21205, 21204, 21206, 21212, 21213, 21214]

        fmpg_sql = 'select PGDate, DP4H, ZYLX from FMGNPG where patientid={}'.format(patient_id)
        fmpg_keys = [21301, 21303, 21302]

        fumoyan_sql = '''select SFRIQI, DJC, FAYY, GLSYangX, GLSYinX, YHXBS, DHXBBL, ZhenJun, PeiYangYX, QiTa,
                   WeiPeiYang, ZLGC from FMYJL where patientid={}'''.format(patient_id)
        fumoyan_keys = [20801, 20802, 20803, 20804, 20805, 20806, 20807, 20808, 20809, 20810, 20811, 20812]

        fttl_sql = 'select SSRIQI, DGLEIXING, SSLEIXING, SSBUWEI, MZFANGSHI from SSJL where patientid={}'.format(
            patient_id)
        fttl_keys = [20401, 20402, 20403, 20404, 20405]

        sdkgr_sql = '''select SFRIQI, FAYY, GLSYangX, GLSYinX, ZhenJun, PeiYangYX, QiTa, WeiPeiYang, ZGQK
                from CKSDGR where patientid={}'''.format(patient_id)
        sdkgr_keys = [20901, 20902, 20903, 20904, 20905, 20906, 20907, 20908, 20909]

        yizhu_sql = '''select SFRIQI, MingCheng, FenLei, YongFa, YongLiang, DanWei, YaoWuYT,TingYongRQ
                        from CGYY where patientid={}'''.format(patient_id)
        yizhu_keys = ['kaiyaoshijian', 'yaowumingcheng', 'guige', 'yongyaopinlv',
                      'yicijiliang', 'danwei', 'yongfa', 'tingzhishijian']

        zhgjl_sql = '''select ZGRIQI, ZGYUANYIN, ZGFENLEI
                from ZGJILU where patientid={}'''.format(patient_id)
        zhgjl_keys = [21001, 21002, 21003]

        siwang_sql = '''select Swrq, Swzyyy, Swcyyy1, Swcyyy2, Swcyyy3, Sqsdtfs, Sqzzdt, Sqzzdtyy, Jsgsyz, Zhycyzrq
                  from SWJL where patientid={}'''.format(patient_id)
        siwang_keys = [22101, 22102, 22103, 22104, 22105, 22106, 22107, 22108, 22109, 22110]

        zhgpg_sql = 'select PGDate, PGZongFen, PGZongFenState from SGAPG where patientid={}'.format(patient_id)
        zhgpg_keys = [21801, 21802, 21803]

        pxzhfcd_sql = 'select PGDate, SBW, SBJW, ETJ, STJ, EGSPZ, JJXPZ from PXZFCL where patientid={}'.format(
            patient_id)

        pxzhfcd_keys = [21922, 21923, 21924, 21925, 21926, 21927, 21928]

        ybzl = self.get_data(ybzl_sql, ybzl_keys)
        self.convert_data(ybzl, 20105)

        bingshi = self.get_data(bingshi_sql, bingshi_keys)
        _ = [i.update({20233: 1}) for i in bingshi]  # 数据来源

        jbqk = self.get_data(jbqk_sql, jbqk_keys)

        zhenduan = self.get_data(zhenduan_sql, zhenduan_keys)
        _ = [i.update({21104: 1}) for i in zhenduan]

        txfa = self.get_data(txfa_sql, txfa_keys)

        txchfxpg = self.get_data(txchfxpg_sql, txchfxpg_keys)

        fmpg = self.get_data(fmpg_sql, fmpg_keys)

        fumoyan = self.get_data(fumoyan_sql, fumoyan_keys)
        self.convert_data(fumoyan, 20811)  # 还有sdk 的呢？

        fttl = self.get_data(fttl_sql, fttl_keys)
        sdkgr = self.get_data(sdkgr_sql, sdkgr_keys)

        yizhu = self.get_data(yizhu_sql, yizhu_keys)
        koufu, zhenji = self.split_yongyaojilu(yizhu)
        yizhu = [{'changqikoufuyongyao': koufu, 'changqizhenjiyongyao': zhenji}]

        zhgjl = self.get_data(zhgjl_sql, zhgjl_keys)
        siwang = self.get_data(siwang_sql, siwang_keys)

        zhgpg = self.get_data(zhgpg_sql, zhgpg_keys)
        pxzhfcd = self.get_data(pxzhfcd_sql, pxzhfcd_keys)

        # 数据表没数据
        yyzplbsds = []
        jlzplbsas = []
        shzlwjkdqolsftm = []
        swzkhwlcd = []

        content = new_content()
        modify_time = ybzl[0].pop('modify_time')
        priority = datetime.strptime(modify_time, '%Y-%m-%d %H:%M:%S')
        content.push_group(ybzl[0], priority.timestamp())

        content1 = new_content()
        content1.push_group([bingshi, jbqk, zhenduan, txfa, txchfxpg, fmpg, fumoyan, fttl, sdkgr, yizhu,
                                zhgpg, pxzhfcd])
        content.merge(content1)

        io.set_output('ybzl', ybzl[0])
        io.set_output('content', content)

        io.push_event('Out')


class XueTouData(Action):
    _id = '507c4cde-10f4-23ea-b977-10231232651a3'
    node_info = {"args": [['patient_id', 'Int', '518543v8-10f4-52ea-b2af-8ce852ackif3'],
                          ['connect', 'Any', '50df5792-3244-11ea-a522-8ce9854c67f3'],
                          ['In', 'Event', 'be723dbe-0053-11ea-8738-8cec4bd83f9f']
                          ],
                 "returns": [
                     ['ybzl', 'Dict', '518543v8-10f4-5421-b2af-8ce8523147f3'],
                     ['content', 'Any', '63254a3v8-10f4-52ea-1230-6325abd347f3'],
                     ['Out', 'Event', 'a9f4fe1f-00b9-3adc-a332-f98ef6327465']]}

    def get_data(self, sql, keys):
        out_data = []
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        while row:
            row_data = dict(zip(keys, row))

            for key, val in row_data.items():
                if val in ['-9999.0', '-9999']:
                    val = None
                if isinstance(val, decimal.Decimal):
                    val = float(val)
                elif isinstance(val, datetime):
                    val = val.strftime('%Y-%m-%d %H:%M:%S')
                row_data[key] = val

            out_data.append(row_data)
            row = self.cursor.fetchone()
        return out_data

    def convert_xingbie(self, array, key):
        for doc in array:
            if '男' in doc[key]:
                doc[key] = 1
            elif '女' in doc[key]:
                doc[key] = 2

    def split_yongyaojilu(self, arry):
        koufu = []
        zhenji = []
        # ['kaiyaoshijian', 'yaowumingcheng', 'yicijiliang', 'danwei', 'yongyaopinlv', 'yongfa']
        for item in arry:
            if item:
                if item.get('yongfa') and '口' in item['yongfa']:
                    koufu.append({
                        10901: item['kaiyaoshijian'],
                        10902: item['yaowumingcheng'],
                        10903: item['yicijiliang'],
                        10904: item['yongyaopinlv'],
                        10905: item['yongfa'],
                        10906: 1,  # 数据来源
                        10907: item['danwei'],
                    })
                elif item.get('guige') and ('针' in item.get('guige') or '注' in item.get('guige')):
                    zhenji.append({
                        11001: item['kaiyaoshijian'],
                        11002: item['yaowumingcheng'],
                        11003: item['yicijiliang'],
                        11004: item['yongyaopinlv'],
                        11005: item['yongfa'],
                        11006: 1,  # 数据来源
                        11007: item['danwei'],
                    })
        return koufu, zhenji

    def __call__(self, args, io):
        patient_id = args['patient_id']
        connect = args['connect']
        self.cursor = connect.cursor()

        ybzl_sql = '''select insure, MenZhenCode, ZhuyuanCode, Name, B.ItemName, IdentityCard, BirthDate, Nationality,
                   Marriage, Stature, Heft, Xiyan, Yinjiu, Shili, C.ItemName, FirstDialyseTime, Income_Time, D.ItemName,
                    E.ItemName, F.ItemName, workaddress, G.ItemName, Address, Telephone, MobilePhone,
                   H.ItemName, ZJXL, PJHZ, JBRS, YHJH, YWYL, JZZK, ZLZ, Patient.modify_time
                   from Patient left join DictionaryItem B on  Patient.Sex = B.ID
                  left join DictionaryItem C on  Patient.PaymentWay = C.ID
                  left join DictionaryItem D on  Patient.Province = D.ID
                  left join DictionaryItem E on  Patient.City = E.ID
                  left join DictionaryItem F on  Patient.District = F.ID
                  left join DictionaryItem G on  Patient.Occupation = G.ID
                  left join DictionaryItem H on  Patient.Culture = H.ID
                  where Patient.id={}'''.format(patient_id)
        ybzl_keys = [10101, 10102, 10103, 10104, 10105, 10114, 10106, 10107, 10108,
                     10109, 10110, 10111, 10112, 10113, 10115, 10116, 10117, 10118,
                     10119, 10120, 10121, 10122, 10123, 10124, 10125, 10126, 10127,
                     10128, 10129, 10130, 10131, 10132, 10133, 'modify_time']

        bingshi_sql = '''select A.DateTime, A.Shenyzshi, A.PDshi,substring(A.Zhusu,1,10000), substring(A.XianBshi,1,10000),
                substring(A.JiWshi,1,10000), A.GMyaow, B.Yingyangzhuangtai, B.TiWei, B.FuZhong, B.Qita from Bingshi A 
                left join Tijian B on A.tijianid=B.ID  where A.Patient_id ={}
                '''.format(patient_id)
        bingshi_keys = [10201, 10206, 10207, 10208, 10209, 10210, 10211, 10202, 10203, 10204]  # 10214]

        xgtl_sql = '''select A.SetupTime, A.StopTime, A.StopReason, A.VesselType,
                  B.ItemName, C.ItemName,  D.ItemName  
                  from DialyseRoute A left join DictionaryItem B on A.VesselRouteType = B.ID
                  left join DictionaryItem C on A.VesselRouteSort = C.ID
                  left join DictionaryItem D on A.vesselroutecztype = D.ID
                   where Patient_id ={}'''.format(patient_id)
        xgtl_keys = [10301, 10306, 10307, 10304, 10302, 10303, 10305]

        lshjl_sql = '''select A.SetupTime, B.ItemName, A.DriedWeight, A.DiFrequency, D.ItemName, E.Name, C.DialyseTime, 
                        C.ReplaceFluidQTY from DialyseScheme A left join DictionaryItem B on A.HeparineType = B.ID
                        right join DialyseSchemeSub C on A.ID = C.Scheme_ID
                        left join DictionaryItem D on C.DialyseType = D.ID
                        left join DializerClass E on C.DialyzerClassID = E.ID
                        where Patient_id ={}'''.format(patient_id)
        lshjl_keys = [10401, 10402, 10403, 10404, 10405, 10406, 10407, 10408]

        crrtjl_sql = '''select A.CRRTtime, B.CRRTjiqi, B.Daoguanxinghao, B.Zhiliaoshijian 
                  from CRRT A left join CRRTTouxifangan B on A.CRRTTouxifangan_id = B.ID 
                  where A.Patient_id ={}'''.format(patient_id)
        crrtjl_keys = [11201, 11202, 11203, 11204]

        hpjl_sql = '''select A.HPtime,B.HPjiqi,B.Daoguanxinghao, B.Zhiliaoshijian 
                  from HP A left join HPTouxifangan B on A.HPTouxifangan_id = B.ID
                  where A.Patient_id ={}'''.format(patient_id)
        hpjl_keys = [11301, 11302, 11303, 11304]

        tpejl_sql = '''select A.TPEtime,B.TPEjiqi,B.Daoguanxinghao, B.Zhiliaoshijian 
                  from TPE A left join TPETouxifangan B on A.TPETouxifangan_id = B.ID 
                  where A.Patient_id ={}'''.format(patient_id)

        tpejl_keys = [11401, 11402, 11403, 11404]

        dfppjl_sql = '''select DFPPtime,DFPPjiqi, Daoguanxinghao, Zhiliaoshijian 
                  from DFPPRecord where Patient_id ={}'''.format(patient_id)
        dfppjl_keys = [11501, 11502, 11503, 11504]

        iajl_sql = '''select IAtime,IAjiqi, Daoguanxinghao, Zhiliaoshijian 
                  from IARecord where Patient_id ={}'''.format(patient_id)
        iajl_keys = [11601, 11602, 11603, 11604]

        txjl_sql = '''select SetupTime ,C.ItemName ,BMI, tqShousuoya,tqShuzhangya ,TQxinlv, 
                  TQHuxi ,Cexueyabuwei , Stime, Jingti, DialyseWeightLater,
                   RealDewater, D.ItemName, Zongzhyliang, thShousuoya,thShuzhangya , THxinlv ,THHuxi 
                  from DialyseRecord A left join DialyseSchemeSub B on A.SubDialyseScheme_ID=B.ID
                  left join DictionaryItem C on B.DialyseType = C.ID
                   left join DictionaryItem D on BloodRouteFlow=D.ID
                   where Patient_id={}'''.format(patient_id)
        txjl_keys = [11101, 11102, 11105, 10501, 10502, 10503, 10504, 10505, 10506,
                     10507, 10508, 10509, 10510, 10511, 10516, 10517, 10518, 10519]

        zhgjl_sql = '''select A.ChangeTime,B.itemName as ChangeStatus,C.itemName as ChangeMode
                  from OUTCOME A left join DictionaryItem B on A.ChangeStatus=B.ID
                  left join DictionaryItem C on A.ChangeMode=C.ID where Patient_id ={}'''.format(patient_id)
        zhgjl_keys = [10601, 10602, 10603]

        zhenduan_sql = '''select DiagnoseTime,DefineName,B.itemName  
                  from Diagnose A left join DictionaryItem B on A.Property=B.ID 
                  where Patient_id ={}'''.format(patient_id)
        zhenduan_keys = [10701, 10702, 10703]

        shshjl_sql = '''select OPS_Time, OPS_Cause, OPS_Type from OPSSchedule 
                  where Patient_id={}'''.format(patient_id)
        shshjl_keys = [10801, 10802, 10803]

        yizhu_sql = '''select MedicineDate, MName, Amount, JiLiang, UMethod, MedicineWay 
                  from MedicineTreatment where Patient_id={}'''.format(patient_id)
        yizhu_keys = ['kaiyaoshijian', 'yaowumingcheng', 'yicijiliang', 'danwei', 'yongyaopinlv', 'yongfa']

        yyzpl_sql = 'select Setup_Time,Point,JieLun from ZungSDS where Patient_id={}'.format(patient_id)
        yyzpl_keys = [11701, 11702, 11703]

        jlzpl_sql = 'select Setup_Time,Point,JieLun from ZungSAS where Patient_id={}'.format(patient_id)
        jlzpl_keys = [11801, 11802, 11803]

        aisengkerenge_sql = '''select Setup_Time, EL,NL,PL,ll,Point 
                            from EPQ where PaTIENT_ID={}'''.format(patient_id)
        aisengkerenge_keys = [11901, 11902, 11903, 11904, 11905, 11906]

        zhengzhuangziping_sql = '''select Setup_Time, QuTiH,QiangPoZZ,RenJiGXMG,YiTu,JiaoLv, DiDui,KongJu,
                                     PianZhi,JingShenBX,QT,YangXingXMS,YinXingXMS, YangXingZZJF,ZongJunF,
                                    Point from SCL90 where PaTIENT_ID={}'''.format(patient_id)

        zhengzhuangziping_keys = [12001, 12004, 12005, 12006, 12007, 12008, 12009, 12010,
                                  12011, 12012, 12013, 12014, 12015, 12016, 12003, 12002]

        lingwushehui_sql = 'select Setup_Time,JiaTingN,JiaTingW,Point from PSSS where PaTIENT_ID={}'.format(patient_id)
        lingwushehui_keys = [12101, 12103, 12104, 12102]

        zhgzhxyyzhkpg_sql = '''select Create_Time, PF, JSZBH, JSSJ, JSLX, WeiChangD, GNYCZYC,
                      GNYC2Z, TJPXDJ, TJJRDJ,TJSZDJ,WLL, WLR from SGA where Patient_id={}'''.format(patient_id)
        zhgzhxyyzhkpg_keys = [12201, 12202, 12203, 12204, 12205, 12206, 12207, 12208, 12209, 12210, 12211, 12212, 12213]

        shhzhlwj_sql = '''select Setup_Time ,Point ,ZhengZhuangYXPF, ShenBingYXPF ,ShenBingFDPF ,
                          GongZuoZTPF ,RenZhiGNPF ,SheHuiYXPF , XingGongNPF ,ShuiMianZLPF ,SheHuiZCLPF ,
                          YiHuRYZCDPF ,ZiWoJKPF , HuanZheMYDPF ,ShenTiGNPF ,SheHuiJSPF ,
                          TengTongDPF ,ZongTiZKPF , QingGanZKPF,SheHuiQGPF ,SheHuiGNPF ,JingLiTLPF
                          from KDQOL where Patient_id={}'''.format(patient_id)
        shhzhlwj_keys = [12401, 12402, 12403, 12404, 12405, 12406, 12407, 12408, 12409, 12410, 12411,
                         12412, 12413, 12414, 12415, 12416, 12417, 12418, 12419, 12420, 12421, 12422]

        pixiazhifan_sql = '''select Setup_Time, ShangBiW,ShangBiJW, ErTouJ,SanTouJ,EGuSP,JianJXP
                               from PXZFCDPG where Patient_id={}'''.format(patient_id)
        pixiazhifan_keys = [12501, 12502, 12503, 12504, 12505, 12506, 12507]

        shwzkpg_sql = '''select Setup_Time,CeDingSJD,ShouTXSWDYK,ECWTBW,TiZhiFang
                      from SWZKPG where Patient_id={}'''.format(patient_id)
        shwzkpg_keys = [12601, 12602, 12603, 12604, 12605]

        wolipinggu_sql = 'select create_time,WoLiZ,WoLiY from WoLiPG where Patient_id={}'.format(patient_id)
        wolipinggu_keys = [12701, 12702, 12703]

        qshqkpg_sql = ''' select Setup_Time,YYZK,XXGGN,MXYZ,GLDX,WKQK,TXCFX
                          from QSQKPG where Patient_id={}'''.format(patient_id)
        qshqkpg_keys = [12801, 12802, 12803, 12804, 12805, 12806, 12807]

        siwang_sql = '''select OutDate, Death_reason, Death_reasonsub1, Death_reasonsub2, Death_reasonsub3, 
                  Siqiantidai_fs, Siqianzhongzhi, Siqianzhiti_yy, Jieshoushen_yz, Zuihouyizhi_rq
                  from DeathRecord where Patient_id={}'''.format(patient_id)
        siwang_keys = [12901, 12902, 12903, 12904, 12905, 12906, 12907, 12908, 12909, 12910]

        ybzl = self.get_data(ybzl_sql, ybzl_keys)
        self.convert_xingbie(ybzl, 10105)  # 性别转化为数字
        

        bingshi = self.get_data(bingshi_sql, bingshi_keys)
        _ = [i.update({10213: 1}) for i in bingshi]  # 数据来源

        xgtl = self.get_data(xgtl_sql, xgtl_keys)
        lshjl = self.get_data(lshjl_sql, lshjl_keys)
        crrtjl = self.get_data(crrtjl_sql, crrtjl_keys)
        hpjl = self.get_data(hpjl_sql, hpjl_keys)
        tpejl = self.get_data(tpejl_sql, tpejl_keys)
        dfppjl = self.get_data(dfppjl_sql, dfppjl_keys)
        iajl = self.get_data(iajl_sql, iajl_keys)
        txjl = self.get_data(txjl_sql, txjl_keys)
        zhgjl = self.get_data(zhgjl_sql, zhgjl_keys)

        zhenduan = self.get_data(zhenduan_sql, zhenduan_keys)
        _ = [i.update({10704: 1}) for i in zhenduan]  # 数据来源

        yizhu = self.get_data(yizhu_sql, yizhu_keys)
        koufu, zhenji = self.split_yongyaojilu(yizhu)
        yizhu = [{'changqikoufuyongyao': koufu, 'changqizhenjiyongyao': zhenji}]

        shshjl = self.get_data(shshjl_sql, shshjl_keys)
        yyzpl = self.get_data(yyzpl_sql, yyzpl_keys)
        jlzpl = self.get_data(jlzpl_sql, jlzpl_keys)
        aisengkerenge = self.get_data(aisengkerenge_sql, aisengkerenge_keys)
        zhengzhuangziping = self.get_data(zhengzhuangziping_sql, zhengzhuangziping_keys)
        lingwushehui = self.get_data(lingwushehui_sql, lingwushehui_keys)
        zhgzhxyyzhkpg = self.get_data(zhgzhxyyzhkpg_sql, zhgzhxyyzhkpg_keys)
        shhzhlwj = self.get_data(shhzhlwj_sql, shhzhlwj_keys)
        pixiazhifan = self.get_data(pixiazhifan_sql, pixiazhifan_keys)
        shwzkpg = self.get_data(shwzkpg_sql, shwzkpg_keys)
        wolipinggu = self.get_data(wolipinggu_sql, wolipinggu_keys)
        qshqkpg = self.get_data(qshqkpg_sql, qshqkpg_keys)
        siwang = self.get_data(siwang_sql, siwang_keys)

        content = new_content()
        modify_time = ybzl[0].pop('modify_time')
        priority = datetime.strptime(modify_time, '%Y-%m-%d %H:%M:%S')
        content.push_group(ybzl[0], priority.timestamp())

        content1 = new_content()
        content1.push_group([bingshi, xgtl, lshjl, crrtjl, hpjl, tpejl, dfppjl, iajl, txjl, zhgjl, zhenduan,
                               shshjl, yizhu, yyzpl, jlzpl, aisengkerenge, zhengzhuangziping, lingwushehui,
                               zhgzhxyyzhkpg, shhzhlwj, pixiazhifan, shwzkpg, wolipinggu, qshqkpg, siwang])
        content.merge(content1)

        io.set_output('ybzl', ybzl[0])
        # io.set_output('data', [ybzl, bingshi, xgtl, lshjl, crrtjl, hpjl, tpejl, dfppjl, iajl, txjl, zhgjl, zhenduan,
        #                        shshjl, yizhu, yyzpl, jlzpl, aisengkerenge, zhengzhuangziping, lingwushehui,
        #                        zhgzhxyyzhkpg, shhzhlwj, pixiazhifan, shwzkpg, wolipinggu, qshqkpg, siwang])
        io.set_output('content', content)
        io.push_event('Out')


class LisData(Action):
    _id = '507c4cde-10f4-23ea-b977-10231253265ac'
    node_info = {"args": [['binglihao', 'String', '518543v8-10f4-52ea-b2af-8c32652145a3'],
                          ['jiuzhenkahao', 'String', '5062541a-3244-11ea-a522-8cec7hac67f3'],
                          ['xingming', 'String', '5653214a-3244-11ea-a522-8cec7hac67f3'],
                          ['chushengriqi', 'String', '5852541a-3244-3251-a522-8cec7hac67f3'],
                          # ['base_sql', 'String', '5065241a-3244-3251-a522-8cec7hac67f3'],
                          ['In', 'Event', '6e02c34c-12f4-11ea-93d0-8541pok7f3']],
                 "returns": [['blh_sql', 'String', '518543v8-10f4-6523-b2af-86521lkh17f3'],
                             ['jzkh_sql', 'String', '965214ac-10f4-5555-b2af-8cec465217f3'],
                             ['xm_rq_sql', 'String', '965214ac-10f4-6523-652a-8851acek17f3'],
                             ['Out', 'Event', '6ec521a8-20f4-123a-90cf-8clack21f7f3']
                             ]}

    def __call__(self, args, io):
        binglihao = args['binglihao']
        jiuzhenkahao = args['jiuzhenkahao']
        xingming = args['xingming']
        chushengriqi = args['chushengriqi']
        # # ['shenfenzhenghao', 'binglihao', 'jiuzhenkahao', 'xingming', 'chushengriqi']

        sql = '''select blh as binglihao, patientid as jiuzhenkahao, birthday as chushengriqi, 
                        PATIENTNAME as xingming, CHECKTIME as shenheshijian, EXAMINAIM
                          as jianyanmudi , SAMPLENO as yangbenhao from L_PATIENTINFO  where '''
        blh_sql = sql + "blh='{}'".format(binglihao)
        jzkh_sql = sql + "patientid='{}'".format(jiuzhenkahao)
        xm_rq_sql = sql + "patientname='{}'".format(xingming)
       
        io.set_output('blh_sql', blh_sql)
        io.set_output('jzkh_sql', jzkh_sql)
        io.set_output('xm_rq_sql', xm_rq_sql)

        io.push_event('Out')


class LisDetailData(Action):
    _id = '507c4cde-10f4-23ea-b977-1026521ac65ac'
    node_info = {"args": [
        ['input_array', 'List', '5652145a-3244-3251-a202-0cec7hac67f3'],
        ['In', 'Event', '6e02c34c-12f4-1325-93d0-7uj36523f3']],
        "returns": [
            ['out_data', 'List', '963210ac-10f4-6523-652a-8ce451317f3'],
            ['Out', 'Event', '6ec32018-20f4-11ea-90cf-8cla6325f7f3']
        ]}

    @classmethod
    def fetch(self, sql):
        import subprocess, os, json, re
        curdir = os.path.split(os.path.realpath(__file__))[0]
        url = 'jbdc:oracle:thin:@192.168.1.7:1521:jyk'
        usr = 'zjhis'
        pwd = 'zjhis'
        cmd = '"{}/../jre1.2/bin/java.exe" -classpath "{}/../oracle";"{}/../oracle/classes12.zip" OracleCon {} {} {} "{}"' \
            .format(curdir, curdir, curdir, url, usr, pwd, sql)

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = p.communicate()

        output = eval(str(stdout, encoding="GB18030"))
        output = [MenZhenDetail.capital_to_lower(i) for i in output]
        return output

    def replace_jieguo_key(self, array):
        new_array = []
        for item in array:
            new_array.append({
                40301: item['jianyanxiangmu'],
                40302: item['ceshijieguo'],
                40303: item['cankaodixian'],
                40304: item['cankaogaoxian'],
                40305: item['jianyanshijian'],
                40203: item['danwei']
            })
        return new_array

    def replace_key(self, array):
        new_array = []
        for item in array:
            new_array.append({
                40106: item['binglihao'],
                40107: item['jiuzhenkahao'],
                40103: item['chushengriqi'],
                40101: item['xingming'],
                40105: item['jianyanmudi'],
                40201: item['yangbenhao'],
                40204: item['shenheshijian'],
                'jieguo': self.replace_jieguo_key(item['jieguo'])
            })
        return new_array

    def __call__(self, args, io):
        input_array = args['input_array']

        sql = '''select B.CHINESENAME as jianyanxiangmu,B.ENGLISHAB as jianyanxiangmuen,TESTRESULT as ceshijieguo,
                REFLO as cankaodixian,REFHI as cankaogaoxian,MEASURETIME as jianyanshijian,L_TESTRESULT.UNIT as danwei 
                from L_TESTRESULT left join L_TESTDESCRIBE B on L_TESTRESULT.TESTID=B.TESTID  where SAMPLENO='{}' '''
        
        seen = set()
        out_data = []
        for item in input_array:
            sample = item['yangbenhao']
            if len(sample) < 8 or sample in seen:  # 过滤无效的sample
                continue
            seen.add(sample)
            jieguo = self.fetch(sql.format(sample))
            item.update({'jieguo': jieguo})
            out_data.append(item)
        print(len(seen), '\n')
        out_data = self.replace_key(out_data)
        io.set_output('out_data', out_data)
        io.push_event('Out')


class MenZhenData(Action):
    _id = '507c4cde-10f4-23ea-b977-1aclecaic65ac'
    node_info = {"args": [['shenfenzhenghao', 'String', '518543v8-10f4-52ea-b2af-8320154a45a3'],
                          ['binglihao', 'String', '518543v8-10f4-52ea-b2af-8201652145a3'],
                          ['jiuzhenkahao', 'String', '5062541a-3244-11ea-a522-aaac7hac67f3'],
                          ['xingming', 'String', '5653214a-3244-11ea-9875-8cec7hac67f3'],
                          ['chushengriqi', 'String', '1025451a-3244-3251-a522-8cec7hac67f3'],
                          # ['base_sql', 'String', '5065241a-3244-3251-a522-8cec730217f3'],
                          ['In', 'Event', '6e02c34c-12f4-11ea-93d0-7uj32917f3']],
                 "returns": [['sfzh_sql', 'String', '518543v8-10f4-6523-b2af-8cec46325ace3'],
                             ['blh_sql', 'String', '518543v8-10f4-6523-b2af-8cec465217f3'],
                             ['jzkh_sql', 'String', '965214ac-10f4-6523-b2af-8cec465217f3'],
                             ['xm_rq_sql', 'String', '965214ac-10f4-6523-652a-8cec465217f3'],
                             ['Out', 'Event', '6ec521a8-20f4-11ea-90cf-8clack21f7f3']
                             ]}

    def __call__(self, args, io):
        shenfenzhenghao = args['shenfenzhenghao']
        binglihao = args['binglihao']
        jiuzhenkahao = args['jiuzhenkahao']
        xingming = args['xingming']
        chushengriqi = args['chushengriqi']
        # ['shenfenzhenghao', 'binglihao', 'jiuzhenkahao', 'xingming', 'chushengriqi']

        sql = '''select sfzh as shenfenzhenghao, bah as binglihao, jzkh as jiuzhenkahao, 
                          xm as xingming, csrq as chushengriqi from gy_brjbxxk where '''
        sfzh_sql = sql + "sfzh='{}'".format(shenfenzhenghao)
        blh_sql = sql + "bah='{}'".format(binglihao)
        jzkh_sql = sql + "jzkh='{}'".format(jiuzhenkahao)
        xm_rq_sql = sql + "xm='{}'".format(xingming)

        io.set_output('sfzh_sql', sfzh_sql)
        io.set_output('blh_sql', blh_sql)
        io.set_output('jzkh_sql', jzkh_sql)
        io.set_output('xm_rq_sql', xm_rq_sql)

        io.push_event('Out')


class MenZhenDetail(Action):
    _id = '507c4cde-10f4-23ea-b977-1acle65214aac'
    node_info = {"args": [['input_array', 'List', '518543v8-10f4-52ea-b2af-8365214845a3'],
                          ['In', 'Event', '6e02c34c-12f4-11ea-93d0-7u652147f3']],
                 "returns": [
                     ['out_data', 'List', '123054ac-10f4-6523-652a-8cec2542154'],
                     ['Out', 'Event', '6ec12058-20f4-11ea-90cf-8clack21f7f3']
                 ]}

    def split_yongyaojilu(self, arry):
        koufu = []
        zhenji = []
        for item in arry:
            if item.get('yongfa') and '口' in item['yongfa']:
                koufu.append({
                    60206: item['kaiyaoshijian'],
                    60201: item['yaowumingcheng'],
                    60202: item['yicijiliang'],
                    60203: item['danwei'],
                    60205: item['yongyaopinlv'],
                    60204: item['yongfa'],
                    60208: item['tingzhishijian'],
                    60209: 2,  # 数据来源
                })
            elif item:
                zhenji.append({
                    60306: item['kaiyaoshijian'],
                    60301: item['yaowumingcheng'],
                    60302: item['yicijiliang'],
                    60303: item['danwei'],
                    60305: item['yongyaopinlv'],
                    60304: item['yongfa'],
                    60308: item['tingzhishijian'],
                    60309: 2,  # 数据来源
                })
        return koufu, zhenji

    @classmethod
    def quchong(self, array):
        seen = set()
        new_array = []
        for a in array:
            temp = tuple(a.items())
            if temp not in seen:
                seen.add(temp)
                new_array.append(a)
        return new_array

    @classmethod
    def capital_to_lower(self, doc):
        new = {}
        for key, value in doc.items():
            new[key.lower()] = value
        return new

    def fetch(self, sql):
        import subprocess, os
        curdir = os.path.split(os.path.realpath(__file__))[0]
        url = 'jbdc:oracle:thin:@192.168.1.114:1521:ORACLE82'
        usr = 'zjhis'
        pwd = 'dec456'
        cmd = '"{}/../jre1.2/bin/java.exe" -classpath "{}/../oracle";"{}/../oracle/classes12.zip" OracleCon {} {} {} "{}"' \
            .format(curdir, curdir, curdir, url, usr, pwd, sql)

        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        stdout, stderr = p.communicate()
        output = eval(str(stdout, encoding="GB18030"))
        output = [self.capital_to_lower(i) for i in output]
        return output

    def replace_key(self, array):
        new_array = []
        for item in array:
            new_array.append({
                60109: item['zhenduanriqi'],
                60110: item['zhenduanmingcheng'],
                60111: 2,
            })
        return new_array

    def replace_base_info_key(self, array):
        new_array = []
        for item in array:
          new_array.append({
            60104: item['xingming'],
            60105: item['shenfenzhenghao'],
            60103: item['binglihao'],
            60102: item['jiuzhenkahao'],
            })
        return new_array

    def __call__(self, args, io):
        input_array = args['input_array']

        zd_sql = '''select ZJ_BL_ZD.ZDMC as zhenduanmingcheng, JZRQ as zhenduanriqi
                            from zj_bl_brbl left join zj_bl_zd on zj_bl_brbl.jzxh=zj_bl_zd.jzxh
                            where JZKH='{}' '''

        yy_sql = '''select mz_cfk1.cfrq as kaiyaoshijian, ypmc as yaowumingcheng, ypgg as guige, 
                          mz_cfk2.YCJL as yicijiliang, mz_cfk2.JLDW as danwei, GYFSMC as yongfa, 
                          mz_cfk2.PL as yongyaopinlv, mz_cfk2.TZSJ as tingzhishijian from mz_cfk1
                          left join mz_cfk2 on mz_cfk1.cfsb=mz_cfk2.cfsb
                          left join GY_YPCDJG on mz_cfk2.JGXH = GY_YPCDJG.xh 
                          left join zj_gyfs on zj_gyfs.GYFSBH=mz_cfk2.FYFS
                          where mz_cfk1.jzkh='{}' '''
        yyjl, zdjl = [], []
        seen = set()
        for item in input_array:
            jzkh = item['jiuzhenkahao']
            if jzkh not in seen:
                seen.add(jzkh)
                zdjl.extend(self.fetch(zd_sql.format(jzkh)))
                yyjl.extend(self.fetch(yy_sql.format(jzkh)))
        print(len(seen), '\n')
        zdjl = self.replace_key(zdjl)

        # 是否要去掉时间戳，去重呢
        result = self.quchong(yyjl)
        koufu, zhenji = self.split_yongyaojilu(result)

        basic_info = self.replace_base_info_key(input_array)

        # io.set_output('zhenduanjilu', zdjl)
        # io.set_output('koufuyao', koufu)
        # io.set_output('zhenjiyao', zhenji)
        io.set_output('out_data', [basic_info, zdjl, koufu, zhenji])
        io.push_event('Out')
