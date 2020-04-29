# coding:utf-8
import os

from PyQt5.QtGui import QFontDatabase, QFont, QFontMetrics
from util import singleton


@singleton
class FontManager(object):
    def __init__(self):
        self.isLoaded = False
        self.customFontName = None
        self.loadFontFamilyFromTTF()
        if self.isLoaded:
            self._customFont = QFont(self.customFontName, 13)
        else:
            self._customFont = QFont("Helvetica [Cronyx]", 13)

    def loadFontFamilyFromTTF(self):
        if not self.isLoaded:
            # load custom font
            dir = os.path.dirname(os.path.abspath(__file__))
            fontId = QFontDatabase.addApplicationFont(dir + '/font/SourceCodePro-Medium.ttf')
            if fontId == -1:
                print('font load failed......')
            loadedFontFamilies = QFontDatabase.applicationFontFamilies(fontId)
            if len(loadedFontFamilies) != 0:
                self.customFontName = loadedFontFamilies[0]

            self._commentFont = QFont("Helvetica [Cronyx]", 13)
            self._freeCommentFont = QFont("Helvetica [Cronyx]", 48)

            self.isLoaded = True

    def customFont(self):
        return self._customFont

    def commentFont(self):
        return self._commentFont

    def freeCommentFont(self):
        return self._freeCommentFont


def measureWidth(string):
    fm = QFontMetrics(FontManager().customFont())
    width = fm.width(string)

    return width
