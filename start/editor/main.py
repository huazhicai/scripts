# coding:utf-8
import sys
import os
import subprocess

from PyQt5.QtCore import pyqtSignal, QSettings, QPoint, QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import *

import widgets
from dlg import ResizeSceneDialog, SaveQuestionDialog, OverrideDialog
import mutil
import data
from font import FontManager
from version import buildDate, version
from mutil import resource_path


class TabWidget(QTabWidget):
    doubleClickSignal = pyqtSignal()
    clickSignal = pyqtSignal()

    def __init__(self):
        super(TabWidget, self).__init__()

    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件,新建一个tab"""
        # 发射鼠标双击信号
        self.doubleClickSignal.emit()

    def mousePressEvent(self, event):
        self.clickSignal.emit()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # 设置控件
        self.setWindowTitle('Node Editor')
        # self.setMinimumSize(600, 400)  # 设置窗口最小尺寸,就是不能拖放比此小
        self.setAcceptDrops(False)  # 设置接受拖放事件

        self.prefs = data.load_prefs()  # 加载偏好设置
        self.mousePosition = (0, 0)
        FontManager()

        self.tabCount = 0  # 初始窗口标题视图数

        self.createTabWidget()  # 创建新new tab
        self.createActions()
        self.createMenus()
        self.createToolBar()

        # 布局管理器对象
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tabWidget)

        # 用于布局的父类控件对象
        self.main_widget = QWidget()
        # 把对象管理器设置给需要布局的父类对象
        self.main_widget.setLayout(layout)

        # 主控件窗口居中
        self.setCentralWidget(self.main_widget)
        self.scriptsData = {}  # 脚本字典数据

        self.readSettings()

    def readSettings(self):
        settings = QSettings('china', 'seven')
        pos = settings.value('pos', QPoint(100, 100))
        size = settings.value('size', QSize(1000, 800))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings('china', 'seven')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    def createTabWidget(self):
        # 新选项卡对象，新定义为了加入一个双击新建信号
        self.tabWidget = TabWidget()
        # 设置大小策略，
        self.tabWidget.setSizePolicy(QSizePolicy.Preferred,
                                     QSizePolicy.Ignored)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setTabShape(QTabWidget.Triangular)
        # 将信号tabCloseRequested连接到指定槽函数，关闭选项卡
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        # self.tabWidget.tabBarClicked.connect(self.switchSpinBox)
        self.tabWidget.currentChanged.connect(self.switchSpinBox)
        # self.tabWidget.doubleClickSignal.connect(self.addTab)   # 双击新建
        self.tabWidget.setStyleSheet('#pane {margin:0; padding: 0}')

    def closeTab(self, index):
        widget = self.tabWidget.widget(index)
        if isinstance(widget, widgets.GraphWidget):
            if not widget.editFlag:
                self.clearTab(index)
                return
            dlg = SaveQuestionDialog(doneChoice=self.whetherToSave,
                                     index=index)
            if dlg.exec_():
                print('save or discard')
            else:
                print('cancel')
        else:
            if widget.editFlag:
                widget.saveTemplate()
            self.clearTab(index)

    def switchSpinBox(self, index):
        widget = self.tabWidget.widget(index)
        if isinstance(widget, widgets.GraphWidget):
            value = widget.spinBoxValue
            self.doubleSpin.setValue(value)

    def addTab(self, isTemplate=False):
        if not isTemplate:
            tab = widgets.GraphWidget()  # 父类标签控件对象
            # 编辑转态改变信号，连接槽函数，更新文江名字
            tab.editStateChanged.connect(self.updateTabCaption)
            # 在视图上的鼠标位置更改信号，连接槽函数，更新鼠标位置
            tab.view.mouseMoved.connect(self.updateMousePosition)
            tempTitle = 'Untitled'
            if self.tabCount > 0:
                tempTitle += ' %d' % self.tabCount
            self.tabCount += 1
            # 调用源码函数，增加新的页面，页面个名字tempTitle. 底层是C++实现的
            self.tabWidget.addTab(tab, tempTitle)
            self.tabWidget.setCurrentWidget(tab)  # 当前的tab就是新建的tab
            self.switchSpinBox(self.tabWidget.currentIndex())  # spinbox初始值
            tab.setScriptMode('new')  # 设置脚本模式
            # 设置页面的提示信息,
            self.tabWidget.setTabToolTip(self.tabWidget.currentIndex(), 'new')
        else:
            tab = widgets.TemplateWidget()
            tab.editStateChanged.connect(self.updateTabCaption)
            tempTitle = mutil.simpleFileName(tab.bindingFile)
            self.tabCount += 1
            self.tabWidget.addTab(tab, tempTitle)
            self.tabWidget.setCurrentWidget(tab)

    def createActions(self):
        self.style = qApp.style()
        self.deleteAction = QAction(
            QIcon(resource_path('./images/delete.png')),
            '&Delete item',
            self,
            shortcut='Del',
            statusTip='Delete a item',
            triggered=self.deleteItem)
        self.runGraphAction = QAction(
            # QIcon(resource_path('./images/run.png')),
            self.style.standardIcon(QStyle.SP_MediaPlay),
            '&Run',
            self,
            shortcut='Shift+F10',
            statusTip='Execute file',
            triggered=self.runGraph)
        self.newGraphAction = QAction(
            QIcon(resource_path('./images/filenew.png')),
            '&New graph',
            self,
            shortcut='Ctrl+N',
            statusTip='create a new graph',
            triggered=self.newGraph)
        self.openGraphAction = QAction(
            QIcon(resource_path('./images/fileopen.png')),
            '&Open graph',
            self,
            shortcut='Ctrl+O',
            statusTip='open a graph',
            triggered=self.openGraph)
        self.openTemplateAction = QAction(
            QIcon(resource_path('./images/template.png')),
            '&Open Template',
            self,
            shortcut='',
            statusTip='open meta template',
            triggered=self.openTemplate)
        self.closeGraphAction = QAction(
            QIcon(resource_path('./images/fileclose.png')),
            '&Close graph',
            self,
            shortcut='Ctrl+W',
            statusTip='close a graph',
            triggered=self.closeGraph)
        self.saveAction = QAction(
            QIcon(resource_path('./images/filesave.png')),
            '&Save',
            self,
            shortcut='Ctrl+S',
            statusTip='save',
            triggered=self.save)
        # self.saveGraphAction = QAction(
        # 	QIcon('./images/filesave.png'),
        # 	'&Save graph',
        # 	self,
        # 	shortcut='Ctrl+S',
        # 	statusTip='save a graph',
        # 	triggered=self.saveGraph)
        self.exportGraphAction = QAction(
            QIcon(resource_path('./images/image.png')),
            '&Export Image',
            self,
            shortcut='',
            statusTip='export to image',
            triggered=self.exportGraph)
        self.convertFileAction = QAction(
            QIcon(resource_path('./images/convert.png')),
            '&Convert File',
            self,
            shortcut='',
            statusTip='convert a graph file',
            triggered=self.convertFile)
        self.exitAction = QAction(
            QIcon(resource_path('./images/exit.png')),
            '&Exit',
            self,
            shortcut='Ctrl+Q',
            statusTip='exit',
            triggered=self.exitMe)
        self.copyAction = QAction(
            QIcon(resource_path('images/copy.png')),
            '&Copy',
            self,
            shortcut='Ctrl+C',
            statusTip='copy an item',
            triggered=self.copyItem)
        self.cutAction = QAction(
            QIcon(resource_path('images/cut.png')),
            '&Cut',
            self,
            shortcut='Ctrl+X',
            statusTip='cut an item',
            triggered=self.cutItem)
        self.pasteAction = QAction(
            QIcon(resource_path('images/paste.png')),
            '&Paste',
            self,
            shortcut='Ctrl+V',
            statusTip='paste an item',
            triggered=self.pasteItem)
        self.resizeSceneAction = QAction(
            QIcon(resource_path('images/resize.png')),
            '&Resize scene',
            self,
            shortcut='',
            statusTip='resize the scene size',
            triggered=self.resizeScene)
        self.undoAction = QAction(
            QIcon(resource_path('images/undo.png')),
            '&Undo',
            self,
            shortcut='Ctrl+Z',
            statusTip='Undo previous operation',
            triggered=self.undo)
        self.redoAction = QAction(
            QIcon(resource_path('images/redo.png')),
            '&Redo',
            self,
            shortcut='Ctrl+Shift+Z',
            statusTip='Redo previous operation',
            triggered=self.redo)
        self.findAction = QAction(
            QIcon(resource_path('images/find.png')),
            '&Find',
            self,
            shortcut='Ctrl+F',
            statusTip='Find item',
            triggered=self.find_)
        self.replaceAction = QAction(
            QIcon(resource_path('images/replace.png')),
            '&Replace',
            self,
            shortcut='Ctrl+H',
            statusTip='Replace some values',
            triggered=self.replace)
        self.aboutAction = QAction(
            QIcon(''),
            '&About',
            self,
            shortcut='',
            statusTip='about me',
            triggered=self.aboutMe)
        QIcon()
        self.stopAction = QAction(
            self.style.standardIcon(QStyle.SP_MediaStop),
            '&Stop',
            self,
            shortcut='',
            statusTip='stop run',
            triggered=self.stopExec)
        self.debugAction = QAction(
            QIcon(resource_path('images/debug.png')),
            '&Debug Run',
            self,
            shortcut='',
            statusTip='debug',
            triggered=self.debugAct)
        self.resumeAction = QAction(
            QIcon(resource_path('images/resume.png')),
            '&Resume',
            self,
            shortcut='',
            statusTip='resume',
            triggered=self.resumeAct)
        self.pauseAction = QAction(
            self.style.standardIcon(QStyle.SP_MediaPause),
            '&Pause',
            self,
            shortcut='',
            statusTip='pause',
            triggered=self.pauseAct)
        self.stepOverAction = QAction(
            QIcon(resource_path('images/debug-step-over.png')),
            '&Step Over',
            self,
            shortcut='',
            statusTip='step over',
            triggered=self.stepOverAct)
        self.startGameClientAction = QAction(
            QIcon(''),
            '&Start Game Client',
            self,
            shortcut='',
            statusTip='start game client',
            triggered=self.startGameClient)
        self.exportTableAction = QAction(
            QIcon(resource_path('images/export_table.png')),
            '&Export Table',
            self,
            shortcut='',
            statusTip='export table',
            triggered=self.exportTable)
        self.runAction = QAction(
            QIcon(resource_path('images/start.png')),
            '&Run in Game',
            self,
            shortcut='',
            statusTip='run in game',
            triggered=self.runInGameWithoutTable)
        self.runActionTable = QAction(
            QIcon(resource_path('images/start.png')),
            '&Run in Game(路点导表)',
            self,
            shortcut='',
            statusTip='run in game',
            triggered=self.runInGameWithTable)
        self.widerAction = QAction(
            QIcon(''),
            '&Wider',
            self,
            shortcut='Ctrl+=',
            statusTip='item wider',
            triggered=self.itemWider)
        self.thinnerAction = QAction(
            QIcon(''),
            '&Thinner',
            self,
            shortcut='Ctrl+-',
            statusTip='item thinner',
            triggered=self.itemThinner)
        self.foldAction = QAction(
            QIcon(resource_path('images/fold.png')),
            '&Fold',
            self,
            shortcut='Ctrl+M',
            statusTip='fold item',
            triggered=self.itemFold)
        self.unfoldAction = QAction(
            QIcon(resource_path('images/unfold.png')),
            '&Unfold',
            self,
            shortcut='Ctrl+Shift+M',
            statusTip='unfold item',
            triggered=self.itemUnfold)
        self.commentAction = QAction(
            QIcon(''),
            '&Comment',
            self,
            shortcut='Ctrl+T',
            statusTip='add comment',
            triggered=self.commentItem)
        self.freeCommentAction = QAction(
            QIcon(''),
            '&Free Comment',
            self,
            shortcut='Ctrl+G',
            statusTip='add free comment',
            triggered=self.freeComment)
        self.showQuickAction = QAction(
            QIcon(''),
            '&Show Quick Bar',
            self,
            shortcut='',
            statusTip='show the quick bar',
            triggered=self.showQuick)
        self.showArgsAction = QAction(
            self.style.standardIcon(QStyle.SP_TitleBarUnshadeButton),
            'Show Args &Panel',
            self,
            shortcut='',
            statusTip='show args panel',
            triggered=self.showArgs)
        self.hideArgsAction = QAction(
            self.style.standardIcon(QStyle.SP_TitleBarShadeButton),
            'Hide Args &Panel',
            self,
            shortcut='',
            statusTip='hide args panel',
            triggered=self.hideArgs)
        self.hideQuickAction = QAction(
            QIcon(''),
            '&Hide Quick Bar',
            self,
            shortcut='',
            statusTip='hide the quick bar',
            triggered=self.hideQuick)
        self.enterFullScreenAction = QAction(
            QIcon(''),
            '&Enter Full Screen',
            self,
            shortcut='',
            statusTip='enter full screen',
            triggered=self.enterFull)
        self.exitFullScreenAction = QAction(
            QIcon(''),
            '&Exit Full Screen',
            self,
            shortcut='Esc',
            statusTip='exit full screen',
            triggered=self.exitFull)

    def newGraph(self):
        self.addTab()

    def updateMousePosition(self, x, y):
        self.mousePosition = (x, y)
        text = '%d,%d' % (x, y)
        self.updateStatusText(text)

    def updateStatusText(self, text):
        self.statusBar().showMessage(text, 2000)
        # self.statusBar().addPermanentWidget(QLabel(text))

    def updateTabCaption(self):
        if self.tabWidget.count() == 0:
            return
        cIndex = self.tabWidget.currentIndex()
        widget = self.tabWidget.currentWidget()
        text = str(self.tabWidget.tabText(cIndex))
        if widget.editFlag and isinstance(widget, widgets.GraphWidget) and (widget.bindingFile is not None):
            scriptname = '%s' % os.path.splitext(os.path.split(widget.bindingFile)[-1])[0]
            # I don't really into this logic here, this really consumes a lot of time, move any item will call this function
            scriptData = widget.getScriptJsonData()
            self.scriptsData[scriptname] = {}
            self.scriptsData[scriptname]['data'] = scriptData
            self.scriptsData[scriptname]['scene'] = widget.scene
            if widget.scene.isGlobal is None:
                if scriptname.find('global') != -1:
                    widget.scene.isGlobal = True
                else:
                    widget.scene.isGlobal = False
        if widget.editFlag:
            # 已编辑，需要加上*号
            if not text.endswith('*'):
                self.tabWidget.setTabText(cIndex, text + '*')
        else:
            # 未编辑，去除*号
            if text.endswith('*'):
                self.tabWidget.setTabText(cIndex, text[:-1])

    def openGraph(self):
        openGraphDir = self.prefs.get('open_graph_dir', None)
        if openGraphDir is None:
            openGraphDir = os.path.join(os.getcwd(), 'graph')

        filenames = QFileDialog.getOpenFileNames(self,
                                                 'Open Graph',
                                                 openGraphDir,
                                                 "All Files (*);;Text Files (*.txt)")
        if type(filenames) == tuple:
            filenames = filenames[0]
        for filename in filenames:
            if filename:
                if type(filename) == tuple or type(filename) == list:
                    filename = str(filename[0])
                else:
                    filename = str(filename)
                if filename.strip() == '':
                    return
                openDir = os.path.dirname(filename)
                self.prefs['open_graph_dir'] = openDir
                # 创建一个新的Tab，在其中打开要打开的图
                tab = widgets.GraphWidget()
                tab.editStateChanged.connect(self.updateTabCaption)
                tab.view.mouseMoved.connect(self.updateMousePosition)
                tab.restoreFromData(filename)
                self.tabCount += 1
                self.tabWidget.addTab(tab, tab.shortFileName())
                self.tabWidget.setCurrentWidget(tab)
                tab.setScriptMode('open')
                self.tabWidget.setTabToolTip(self.tabWidget.currentIndex(), filename)
                scriptname = '%s' % os.path.splitext(os.path.split(tab.bindingFile)[-1])[0]
                scriptData = tab.getScriptJsonData()
                self.scriptsData[scriptname] = {}
                self.scriptsData[scriptname]['data'] = scriptData
                self.scriptsData[scriptname]['scene'] = tab.scene

    def openTemplate(self):
        self.addTab(isTemplate=True)

    def whetherToSave(self, choice, index=None):
        if choice == 'Cancel':
            return

        if choice == 'Save':
            # 保存图形
            if index is None:
                widget = self.tabWidget.currentWidget()
                if isinstance(widget, widgets.GraphWidget):
                    # 保存当前tab中的图形
                    if self.saveGraph():
                        currentIndex = self.tabWidget.currentIndex()
                        self.clearTab(currentIndex)
                else:
                    currentIndex = self.tabWidget.currentIndex()
                    widget.saveTemplate()
                    self.clearTab(currentIndex)
            else:
                widget = self.tabWidget.widget(index)
                if isinstance(widget, widgets.GraphWidget):
                    # 保存给定index中的图形
                    if self.saveGraphAt(index):
                        self.clearTab(index)
                else:
                    widget.saveTemplate()
                    self.clearTab(index)
        else:
            if index is None:
                # 舍弃当前图形
                currentIndex = self.tabWidget.currentIndex()
                self.clearTab(currentIndex)
            else:
                # 舍弃给定Index的图形
                self.clearTab(index)

    def closeGraph(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        if not graphWidget.editFlag:
            cIndex = self.tabWidget.currentIndex()
            self.clearTab(cIndex)
            return

        dlg = SaveQuestionDialog(doneChoice=self.whetherToSave)
        if dlg.exec_():
            print('save or discard')
        else:
            print('canceled')

    def runGraph(self):
        """执行当前选中的文件"""
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return
        # self.runGraphAction.setIcon(QIcon(resource_path('images/run1.png')))
        self.runGraphAction.setDisabled(True)
        graphWidget.runGraph()
        graphWidget.runFinished.connect(lambda: self.runGraphAction.setEnabled(True))

    def saveGraph(self):
        """
        保存当前选中的tab中的内容，到文件中
        """
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        # 如果未编辑过，不需要保存
        # if not graphWidget.editFlag:
        #	return True

        if graphWidget.bindingFile is not None:
            graphWidget.saveGraph(graphWidget.bindingFile)
            return True

        saveGraphDir = self.prefs.get('save_graph_dir', None)
        if saveGraphDir is None:
            saveGraphDir = os.path.join(os.getcwd(), 'graph')

        filename = QFileDialog.getSaveFileName(self,
                                               'Save Graph',
                                               saveGraphDir,
                                               "Json Files (*.json);;All Files (*)")
        if filename:
            if type(filename) == tuple:
                filename = str(filename[0])
            else:
                filename = str(filename)

            if filename.strip() == '':
                # 文件名为空，未获得文件名，标识因取消而不保存
                return False
            if filename.endswith('.txt'):
                filename = filename.strip('.txt')

            if not filename.endswith('.json'):
                filename = filename + '.json'

            if os.path.exists(filename):
                # 此文件已存在
                overrideDlg = OverrideDialog()
                if overrideDlg.exec_():
                    # 同意覆盖
                    saveDir = os.path.dirname(filename)
                    self.prefs['save_graph_dir'] = saveDir

                    graphWidget = self.tabWidget.currentWidget()
                    graphWidget.saveGraph(filename)
                    cIndex = self.tabWidget.currentIndex()
                    self.tabWidget.setTabText(cIndex,
                                              graphWidget.shortFileName())
                    return True
                else:
                    # 不同意覆盖
                    return False
            else:
                # 此文件未存在
                saveDir = os.path.dirname(filename)
                self.prefs['save_graph_dir'] = saveDir

                graphWidget = self.tabWidget.currentWidget()
                graphWidget.saveGraph(filename)
                cIndex = self.tabWidget.currentIndex()
                self.tabWidget.setTabText(cIndex, graphWidget.shortFileName())
                return True
        else:
            return False

    def saveGraphAt(self, index):
        """
        保存给定index对应的tab中的内容，到文件中
        """
        graphWidget = self.tabWidget.widget(index)
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        # 如果未编辑过，不需要保存
        if not graphWidget.editFlag:
            return True

        if graphWidget.bindingFile is not None:
            graphWidget.saveGraph(graphWidget.bindingFile)
            return True

        saveGraphDir = self.prefs.get('save_graph_dir', None)
        if saveGraphDir is None:
            saveGraphDir = os.path.join(os.getcwd(), 'graph')

        filename = QFileDialog.getSaveFileName(self,
                                               'Save Graph',
                                               saveGraphDir,
                                               "All Files (*);;Text Files (*.txt)")
        if filename:
            if type(filename) == tuple:
                filename = str(filename[0])
            else:
                filename = str(filename)

            if filename.strip() == '':
                # 文件名为空，未获得文件名，标识因取消而不保存
                return False

            if not filename.endswith('.json'):
                filename = filename + '.json'

            if os.path.exists(filename):
                # 保存的文件已经存在
                overrideDlg = OverrideDialog()
                if overrideDlg.exec_():
                    # 同意覆盖
                    saveDir = os.path.dirname(filename)
                    self.prefs['save_graph_dir'] = saveDir

                    graphWidget = self.tabWidget.widget(index)
                    graphWidget.saveGraph(filename)
                    self.tabWidget.setTabText(index,
                                              graphWidget.shortFileName())
                    return True
                else:
                    # 不同意覆盖
                    return False
            else:
                # 保存的文件未存在
                saveDir = os.path.dirname(filename)
                self.prefs['save_graph_dir'] = saveDir

                graphWidget = self.tabWidget.widget(index)
                graphWidget.saveGraph(filename)
                self.tabWidget.setTabText(index,
                                          graphWidget.shortFileName())
                return True
        else:
            return False

    def exportGraph(self):
        exportImageDir = self.prefs.get('export_image_dir', None)
        if exportImageDir is None:
            exportImageDir = os.path.join(os.getcwd(), 'export/pics')
            if not os.path.exists(exportImageDir):
                os.mkdir(exportImageDir)

        filename = QFileDialog.getSaveFileName(self,
                                               'Export as Image',
                                               exportImageDir)

        if filename:
            if type(filename) == tuple:
                filename = str(filename[0])
            else:
                filename = str(filename)

            if filename.strip() == '':
                return

            exportDir = os.path.dirname(filename)
            self.prefs['export_image_dir'] = exportDir

            if not filename.endswith('.png'):
                filename = filename + '.png'

            graphWidget = self.tabWidget.currentWidget()
            graphWidget.exportGraph(filename)

    def startGameClient(self):
        """
        启动游戏客户端
        """
        gameClientDir = self.prefs.get('game_client_dir', None)
        if gameClientDir is None:
            # 人工选择出游戏客户端所在的目录
            filename = QFileDialog.getOpenFileName(self,
                                                   'Find Game Client',
                                                   '.',
                                                   'All Files (*);;Text Files (*.txt)')
            if type(filename) == tuple:
                filename = str(filename[0])
            else:
                filename = str(filename)

            if filename.strip() == '':
                # 没选择到游戏客户端的可执行文件，
                # 打开游戏客户端的工作到此结束，否则会出错
                return
            gameClientDir = os.path.dirname(filename)
            self.prefs['game_client_dir'] = gameClientDir

        currentDir = os.getcwd()
        os.chdir('%s' % self.prefs['game_client_dir'])
        child = subprocess.Popen('client.exe', shell=True)
        os.chdir(currentDir)

    def clearTab(self, index):
        widget = self.tabWidget.widget(index)
        if isinstance(widget, widgets.GraphWidget):
            widget.closeWidget(self.scriptsData)
        else:
            widget.closeWidget()
        self.tabWidget.removeTab(index)

    def resizeScene(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        dlg = ResizeSceneDialog(graphWidget.sceneWidth,
                                graphWidget.sceneHeight,
                                graphWidget.resizeScene)

        if dlg.exec_():
            print('resize ok')
        else:
            print('resize cancel')

    def undo(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return
        graphWidget.scene.undoStack.undo()
        graphWidget.updateEdit(True)

    def redo(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.scene.undoStack.redo()
        graphWidget.updateEdit(True)

    def find_(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.find_()

    def replace(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return
        graphWidget.replace()

    def copyItem(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.copyItem()

    def cutItem(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.cutItem()

    def pasteItem(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.pasteItem(self.mousePosition)

    def exportTable(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.exportTable()

    def runInGameWithTable(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.runInGame(self.scriptsData, withTable=True)

    def runInGameWithoutTable(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.runInGame(self.scriptsData, withTable=False)

    def save(self):
        widget = self.tabWidget.currentWidget()
        if isinstance(widget, widgets.TemplateWidget):
            widget.saveTemplate()
        else:
            self.saveGraph()

    def createToolBar(self):
        self.fileToolBar = self.addToolBar("File")
        # self.fileToolBar.setToolButtonStyle()
        self.fileToolBar.setIconSize(QSize(20, 20))
        self.fileToolBar.addAction(self.newGraphAction)
        self.fileToolBar.addAction(self.saveAction)
        self.fileToolBar.addAction(self.openGraphAction)
        self.fileToolBar.addSeparator()

        # self.editToolBar = self.addToolBar("Edit")
        self.fileToolBar.addAction(self.copyAction)
        self.fileToolBar.addAction(self.pasteAction)
        self.fileToolBar.addAction(self.cutAction)
        self.fileToolBar.addAction(self.deleteAction)

        # self.viewToolBar = self.addToolBar("View")
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.showArgsAction)
        self.fileToolBar.addAction(self.hideArgsAction)
        self.fileToolBar.addSeparator()

        self.fileToolBar.addWidget(QLabel(" Interval:"))
        self.doubleSpin = QDoubleSpinBox()
        self.doubleSpin.resize(20, 40)
        self.doubleSpin.setRange(0.00, 3.00)
        self.doubleSpin.setSingleStep(0.50)
        self.fileToolBar.addWidget(self.doubleSpin)
        self.doubleSpin.valueChanged.connect(self.updateSpinValue)

        # spacer = QWidget()
        # spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.fileToolBar.addWidget(spacer)
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.runGraphAction)
        self.fileToolBar.addAction(self.stopAction)
        # self.stopAction.setIcon()
        self.fileToolBar.addSeparator()
        self.fileToolBar.addAction(self.debugAction)
        self.fileToolBar.addAction(self.resumeAction)
        self.fileToolBar.addAction(self.pauseAction)
        self.fileToolBar.addAction(self.stepOverAction)
        # print(self.fileToolBar.children())

    def updateSpinValue(self, value):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.updateSpinBoxValue(value)

    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu('&File')
        self.fileMenu.addAction(self.newGraphAction)
        self.fileMenu.addAction(self.runGraphAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openGraphAction)
        self.fileMenu.addAction(self.openTemplateAction)
        # self.fileMenu.addAction(self.saveGraphAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addAction(self.closeGraphAction)
        self.fileMenu.addAction(self.exportGraphAction)
        self.fileMenu.addAction(self.convertFileAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAction)

        self.editMenu = self.menuBar().addMenu('&Edit')
        self.editMenu.addAction(self.deleteAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.undoAction)
        self.editMenu.addAction(self.redoAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.copyAction)
        self.editMenu.addAction(self.cutAction)
        self.editMenu.addAction(self.pasteAction)
        self.fileMenu.addSeparator()
        self.editMenu.addAction(self.findAction)
        self.editMenu.addAction(self.replaceAction)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.resizeSceneAction)

        self.itemMenu = self.menuBar().addMenu('&Item')
        self.itemMenu.addAction(self.widerAction)
        self.itemMenu.addAction(self.thinnerAction)
        self.itemMenu.addSeparator()
        self.itemMenu.addAction(self.foldAction)
        self.itemMenu.addAction(self.unfoldAction)
        self.itemMenu.addSeparator()
        self.itemMenu.addAction(self.commentAction)
        self.itemMenu.addAction(self.freeCommentAction)

        self.viewMenu = self.menuBar().addMenu('&View')
        self.viewMenu.addAction(self.showArgsAction)
        self.viewMenu.addAction(self.hideArgsAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.showQuickAction)
        self.viewMenu.addAction(self.hideQuickAction)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.enterFullScreenAction)
        self.viewMenu.addAction(self.exitFullScreenAction)

        self.aboutMenu = self.menuBar().addMenu('&Help')
        self.aboutMenu.addAction(self.aboutAction)
        self.aboutMenu.addAction(self.stopAction)
        # self.stopAction.setDisabled(True)
        self.aboutMenu.addAction(self.debugAction)
        self.aboutMenu.addAction(self.resumeAction)
        # self.resumeAction.setDisabled(True)
        self.aboutMenu.addAction(self.pauseAction)
        # self.pauseAction.setDisabled(True)

    def deleteItem(self):
        # 当前标签场景
        graphicWidget = self.tabWidget.currentWidget()
        if not isinstance(graphicWidget, widgets.GraphWidget):
            return

        graphicWidget.deleteItem()

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        for url in urls:
            filename = str(url.path())
            graphWidget = self.tabWidget.currentWidget()
            graphWidget.restoreFromData(filename)
            cIndex = self.tabWidget.currentIndex()
            self.tabWidget.setTabText(cIndex, graphWidget.shortFileName())

    def maybeSaveTabs(self):
        """
        关闭前检查每个tab中的文件是否已经保存了
        """
        self.tabWidget.currentChanged.disconnect(self.switchSpinBox)

        if self.tabWidget.count() == 0:
            return True

        for i in range(self.tabWidget.count()):
            graphWidget = self.tabWidget.widget(i)

            if graphWidget is None:
                continue

            graphWidget.read_data_thread.terminate()
            if not graphWidget.editFlag:
                continue
            dlg = SaveQuestionDialog(doneChoice=self.whetherToSave,
                                     index=i)
            if dlg.exec_():
                # print('save or discard')
                return True
            else:
                return False
        return True

    def closeEvent(self, event):
        if self.maybeSaveTabs():
            self.savePrefs()
            event.accept()
            # super().closeEvent()
        else:
            event.ignore()
        # super().closeEvent()

    def convertFile(self):
        openGraphDir = self.prefs.get('open_graph_dir', None)
        if openGraphDir is None:
            openGraphDir = os.path.join(os.getcwd(), 'graph')

        filename = QFileDialog.getOpenFileName(self,
                                               'Open Graph',
                                               openGraphDir,
                                               "All Files (*);;Text Files (*.txt)")
        if filename:
            if type(filename) == tuple:
                filename = str(filename[0])
            else:
                filename = str(filename)

            if filename.strip() == '':
                return

            from A_Exporter import convertFile
            # from backcompat import convertFile

            if convertFile(filename):
                QMessageBox.information(None,
                                        'Info',
                                        '转换文件成功!',
                                        QMessageBox.Ok)

            else:
                QMessageBox.information(None,
                                        'Warning',
                                        '转换文件失败',
                                        QMessageBox.Ok)

    def exitMe(self):
        self.maybeSaveTabs()
        self.savePrefs()
        sys.exit()

    def savePrefs(self):
        """保存偏好设置"""
        # self.prefs['scene_width'] = self.sceneWidth
        # self.prefs['scene_height'] = self.sceneHeight
        self.writeSettings()
        data.save_prefs(self.prefs)

    def stopExec(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return
        graphWidget.killChildProcess()

    def debugAct(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        self.debugAction.setDisabled(True)
        # self.debugAction.setIcon(QIcon(resource_path('images/debug1.png')))
        graphWidget.debugRun()
        # graphWidget.runFinished.connect(lambda: self.debugAction.setIcon(QIcon(resource_path('images/debug.png'))))
        graphWidget.runFinished.connect(lambda: self.debugAction.setEnabled(True))

    def resumeAct(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return
        graphWidget.resumeSpider()

    def pauseAct(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return
        graphWidget.pauseSpider()

    def stepOverAct(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return
        graphWidget.stepOverSpider()

    def aboutMe(self):
        QMessageBox.information(self,
                                '关于',
                                '节点编辑工具 - ' + buildDate + '\nSVN 版本 - ' + version,
                                QMessageBox.Yes)

    def itemWider(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.itemWider()

    def itemThinner(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.itemThinner()

    def commentItem(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.commentItem()

    def freeComment(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.freeComment()

    def showQuick(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.blankWidget.show()

    def hideQuick(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.blankWidget.hide()

    def showArgs(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.args_panel.show()

    def hideArgs(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.args_panel.hide()

    def enterFull(self):
        self.showFullScroeen()

    def exitFull(self):
        self.showNormal()

    def itemFold(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.itemFold()

    def itemUnfold(self):
        graphWidget = self.tabWidget.currentWidget()
        if not isinstance(graphWidget, widgets.GraphWidget):
            return

        graphWidget.itemUnfold()


# def main():
#     # 1.创建一个应用程序对象，传入参数列表
#     app = QApplication(sys.argv)
#     # 2. 控件的操作
#     # 2.1 创建控件
#     mainWindow = MainWindow()
#     # 2.2 设置控件
#     screenRect = app.desktop().screenGeometry()  # 屏幕几何位置、尺寸(0, 0, 1440, 900)
#     # screenRect.center() 屏幕中心坐标（719，449）
#     # 窗口中心点移动到屏幕中心点
#     mainWindow.move(screenRect.center() - mainWindow.rect().center())
#     # 2.3 展示控件
#
#     mainWindow.setGeometry(100, 100, 1200, 800)  # 不小于最小尺寸setMinimize
#     mainWindow.show()
#
#     # 3. 应用程序的执行，进入消息循环
#     sys.exit(app.exec_())

def main():
    app = QApplication(sys.argv)

    main_wnd = MainWindow()

    main_wnd.show()

    sys.exit(app.exec_())


def getScriptMode():
    if len(sys.argv) == 2:
        return str(sys.argv[1]).lower()
    else:
        return None

# if __name__ == '__main__':
#     main()
# print('Please execute run.py!')
