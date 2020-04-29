class Filter(object):
    def __init__(self, sfzh, blh, jzkh, xm, csrq, obj_keys):
        self.sfzh = sfzh
        self.blh = blh
        self.jzkh = jzkh
        self.xm = xm
        self.csrq = csrq 
        self.obj_keys = obj_keys

    def filter_data(data):
        shenfenzhenghao = data.get(self.obj_keys[0])
        binglihao = data.get(self.obj_keys[1])
        jiuzhenkahao = data.get(self.obj_keys[2])
        xingming = data.get(self.obj_keys[3])
        chushengriqi = data.get(self.obj_keys[4])

        if shenfenzhenghao and self.sfzh and shenfenzhenghao == sfz:
            return True 
        
        if binglihao and self.blh and binglihao == self.blh:
            return True 

        if jiuzhenkahao and self.jzkh and jiuzhenkahao == self.jzkh:
            return True 

        if not (shenfenzhenghao or binglihao or jiuzhenkahao):
            if self.xm and self.csrq and xingming and chushengriqi:
                if self.xm == xingming and self.csrq.strip()[:10] == chushengriqi.strip()[:10]:
                    return True 
            