# coding:utf-8
from PyQt5.QtGui import QColor

from util import singleton
import data


@singleton
class ColorManager(object):
    def __init__(self):
        self.colorData = self.loadColorData()

    def getColor(self, loc_key, kind_key):
        """
        给定部位 location key : loc_key
            类别 kind key : kind_key
        可以确定在该区域，属于该类别的背景颜色
        """
        loc_colors = self.colorData.get(loc_key, None)
        if loc_colors is None:
            return None

        color = loc_colors.get(kind_key, None)
        return color if color is not None else loc_colors.get('default', None)

    def loadColorData(self):
        raw_data = data.load_color_config()
        color_data = {}
        for loc_key in raw_data:
            color_data[loc_key] = {}
            for kind_key in raw_data[loc_key]:
                conf = raw_data[loc_key][kind_key]
                color_data[loc_key][kind_key] = QColor(
                    conf['red'],
                    conf['green'],
                    conf['blue'],
                    conf['alpha']
                )

        return color_data
