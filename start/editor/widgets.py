# coding:utf-8
import sys
import os
import json
import traceback
import multiprocessing

from PyQt5.Qt import Qt
from PyQt5.QtCore import pyqtSignal, QRectF, QTimer, QThread
from PyQt5.QtGui import QColor, QImage, QPainter
from PyQt5.QtWidgets import *

from controller import ControllerManager
from scene import DiagramScene, TemplateScene
from view import DiagramView
from dlg import ErrorConsoleDialog, FindDialog, ReplaceDialog
from functools import partial

# 共用一个导表工具
from editor.A_Exporter import single_file_export

sys.path.append(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir), 'csv2py'))
from ActivityScriptExporter import editor_validate_and_export
import logger


class GraphWidget(QWidget):
    editStateChanged = pyqtSignal()
    runFinished = pyqtSignal()

    def __init__(self, parent=None):
        super(GraphWidget, self).__init__(parent)

        self.editFlag = False  # 未在编辑转态

        self.controllerKey = ControllerManager().addController()
        self.sceneWidth = 10000
        self.sceneHeight = 10000
        self.bindingFile = None

        # 创建图形场景对象，传递控制键参数
        self.scene = DiagramScene(self.controllerKey)
        self.scene.setSceneRect(QRectF(-self.sceneWidth / 2.0, -self.sceneHeight / 2.0,
                                       self.sceneWidth, self.sceneHeight))
        # 将信号itemSelected连接到指定槽函数
        self.scene.itemSelected.connect(self.itemSelected)
        self.scene.resetModeSignal.connect(self.modeReseted)
        self.scene.editSignal.connect(self.sceneEdited)

        # 创建图形视口对象，传入图形场景作为对象参数
        self.view = DiagramView(self.scene)
        # self.view.setBackgroundBrush(QColor(230, 200, 167))
        # self.view.setBackgroundBrush(QColor(41, 41, 41))
        self.view.setMouseTracking(True)  # 视图鼠标跟踪

        # 创建水平布局管理器对象
        layout = QHBoxLayout()
        # 视图控件对象添加到布局管理器中
        layout.addWidget(self.view)
        # 把布局管理器设置给需要布局的父控件
        self.setLayout(layout)

        # 参数面板控件
        self.args_panel = ArgsDockWidget(self)
        self.args_panel.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.SubWindow)

        # self.args_panel.args_tab.setColumnWidth(0, 100)
        # self.args_panel.args_tab.setColumnWidth(1, 150)
        self.args_panel.setGeometry(0, 0, 250, 200)
        self.args_panel.hide()

        # 空白控件，新建节点快捷栏
        self.blankWidget = QuickDockWidget()
        self.blankWidget.setParent(self)
        self.blankWidget.resize(900, 80)
        self.blankWidget.show()
        self.blankWidget.raise_()
        self.blankWidget.hide()  # 默认掩藏节点快捷栏

        self.findResult = set()
        self.findResultItems = []
        self.targetNode = None
        self.prevNodeList = []
        self.nextNodeList = []
        self.prevEdgeList = []
        self.nextEdgeList = []

        self.controller = ControllerManager().getController(self.controllerKey)
        self.controller.setScene(self.scene)

        self.nameIndex = {}
        self.valueIndex = {}
        self.commentIndex = {}
        self.allNodes = set()

        self.logger = logger.getLogger('GraphWidget')

        self.spinBoxValue = 0.00
        self.process = None
        self.run_mode = None

        self.parent_conn, self.child_conn = multiprocessing.Pipe()
        # 线程 读取管道数据
        # self.thread_ = threading.Thread(target=self.receive_data)
        # self.thread_.setDaemon(True)
        # self.thread_.start()
        self.read_data_thread = ReadDataThread(self.parent_conn, self)
        self.read_data_thread.start()
        self.read_data_thread.dataSignal[dict].connect(self.receive_data)
        self.read_data_thread.dataSignal[str].connect(self.finishedSlot)

    def updateSpinBoxValue(self, value):
        self.spinBoxValue = value

    def setScriptMode(self, opentype):
        if opentype != 'new':
            filename = '%s' % os.path.splitext(os.path.split(self.bindingFile)[-1])[0]
            if filename.endswith('_c') or filename.endswith('_client'):
                if filename.find('global') != -1:
                    self.scene.isGlobal = True
                else:
                    self.scene.isGlobal = False
        self.scene.createContextMenu()

    def openGraph(self, filename):
        controller = ControllerManager().getController(self.controllerKey)
        controller.restoreFromData(self.scene, filename=filename)
        self.updateEdit(False)

    def runGraph(self):
        controller = ControllerManager().getController(self.controllerKey)
        self.uuidIndex = {node.uuid: node for node in controller.nodes}

        data = controller.getData()
        config_data = single_file_export(data)

        if self.process and self.process.is_alive():
            self.killChildProcess()

        # 开启爬虫子进程
        from run import crawl

        self.parent_conn.send(self.spinBoxValue)  # 模块间隔时间
        self.process = multiprocessing.Process(target=crawl, args=(config_data, self.child_conn))
        self.startSlot()  # 初始设置
        self.process.start()

    def receive_data(self, data):
        if isinstance(data, str) and self.uuidIndex.get(data, None):
            self.lightRunNode(data)  # 高亮
            
        if isinstance(data, dict) and data.get('node_index', None) and data.get('exception', None) is None:
            self.lightRunNode(data['node_index'])  # 高亮


            if data.pop('node_index') in self.controller.getBreakPoints():
                # print(data)
                pass 

            # data.pop('node_index')
            # self.args_panel.args_tab.clearContents()  # clear history
            # if len(data):
                # self.args_panel.args_tab.setRowCount(len(data))

            #     for idx, item in enumerate(data.items()):
            #         self.args_panel.args_tab.setItem(idx, 0, QTableWidgetItem(str(item[0])))
            #         self.args_panel.args_tab.setItem(idx, 1, QTableWidgetItem(str(item[1])))

        if data.get('exception', None):
            self.lightExceptionNode(data['node_index'])

    def sendBreakPoints(self):
        # controller = ControllerManager().getController(self.controllerKey)
        breakPoints = self.controller.getBreakPoints()
        self.parent_conn.send(breakPoints)

    def debugRun(self):
        if self.process and self.process.is_alive():
            rb = QMessageBox.question(None, 'Process is running',
                                      'Do you want to STOP and RERUN',
                                      QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
            if rb == QMessageBox.No:
                return
            self.killChildProcess()

        self.run_mode = 'debug'
        self.sendBreakPoints()
        self.runGraph()

    def pauseSpider(self):
        if self.run_mode == 'debug':
            self.parent_conn.send('pause')

    def stepOverSpider(self):
        if self.run_mode == 'debug':
            self.parent_conn.send('step over')

    def resumeSpider(self):
        if self.run_mode == 'debug':
            self.sendBreakPoints()
            self.parent_conn.send('resume')

    def startSlot(self):
        for node in self.uuidIndex.values():
            self.prev_node = node
            break
        print('****************** Started! *******************\n')

    def finishedSlot(self):
        for node in self.uuidIndex.values():
            node.removeHighLight()

        self.args_panel.args_tab.clearContents()
        self.args_panel.args_tab.setRowCount(0)
        self.run_mode = None
        # self.process.terminate()
        self.runFinished.emit()
        print('\n****************** Finished! ******************')

    def lightRunNode(self, node_index):
        self.prev_node.removeHighLight()
        self.uuidIndex[node_index].setHighLight(1)
        self.prev_node = self.uuidIndex[node_index]

    def lightExceptionNode(self, node_index):
        self.uuidIndex[node_index].setHighLight(2)

    def killChildProcess(self):
        if self.process:
            self.process.terminate()
            # self.prev_node.removeHighLight()
            self.finishedSlot()

    def saveGraph(self, filename):
        controller = ControllerManager().getController(self.controllerKey)
        controller.saveGraph(filename=filename)
        if filename != self.bindingFile:
            self.bindingFile = filename
        self.updateEdit(False)

    def exportGraph(self, filename):
        self.scene.clearSelection()
        imageBoundingRect = self.scene.itemsBoundingRect()
        topLeft = imageBoundingRect.topLeft()
        size = imageBoundingRect.size()
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.timage = QImage(self.scene.sceneRect().size().toSize(),
                             QImage.Format_ARGB32)
        self.timage.fill(Qt.transparent)

        painter = QPainter(self.timage)
        self.scene.render(painter)
        self.timage.save('%s' % filename)
        self.updateEdit(True)

    def restoreFromData(self, filename):
        controller = ControllerManager().getController(self.controllerKey)
        if controller.restoreFromData(self.scene,
                                      filename=filename):
            self.bindingFile = filename
            self.updateEdit(False)

    def resizeScene(self, width, height):
        self.sceneWidth = width
        self.sceneHeight = height
        self.scene.setSceneRect(QRectF(-self.sceneWidth / 2.0,
                                       -self.sceneHeight / 2.0,
                                       self.sceneWidth,
                                       self.sceneHeight))
        self.updateEdit(True)

    def exportTable(self):
        """
        导表
        """
        # how to get the prefs info elegantly
        prefs = self.parentWidget().parentWidget().parentWidget().parentWidget().prefs
        csv2pyPath = prefs['open_graph_dir'].replace('levelscripts', '')
        print(csv2pyPath)
        gameClientDir = prefs.get('game_client_dir', None)
        if not gameClientDir:
            filename = QFileDialog.getOpenFileName(self,
                                                   '选择client.exe文件，用于生成动画信息和本地路点信息',
                                                   '.',
                                                   'exe(*.exe)')
            if type(filename) == tuple:
                filename = str(filename[0])
            else:
                filename = str(filename)

            gameClientDir = os.path.dirname(filename)
            prefs['game_client_dir'] = gameClientDir
        resPath = os.path.join(gameClientDir, 'res')
        resDict = self.localValidate(resPath)
        if resDict is None:
            return
        exportResult = resDict['result']
        errors = resDict['errors']

        dlg = ErrorConsoleDialog(errors, self.locateError, self)
        dlg.setAttribute(Qt.WA_DeleteOnClose)
        dlg.setModal(False)
        dlg.show()
        dlg.raise_()
        dlg.activateWindow()

        if exportResult is None:
            return

        if not os.path.exists('export/tables'):
            os.mkdir('export/tables')

        if self.bindingFile is not None:
            filename = '%s.py' % os.path.splitext(os.path.split(self.bindingFile)[-1])[0]
            fullpath = 'export/tables/%s' % filename
            with open(fullpath, 'w') as f:
                json.dump(exportResult, f)
        else:
            fullpath = 'export/tables/tmp.py'
            with open(fullpath, 'w') as f:
                json.dump(exportResult, f)

    def locateError(self, iD, subItemId):
        """
        根据给定的iD和subItemId来定位错误
        """
        self.scene.locateError(iD, subItemId)

    def itemSelected(self):
        pass

    def modeReseted(self):
        pass

    def localValidate(self, resPath):
        """
        进行就地校验
        """
        # 如果还没有保存文件，需要先保存文件
        if self.bindingFile is None or self.editFlag:
            QMessageBox.information(None,
                                    'Info',
                                    '请先保存文件!',
                                    QMessageBox.Ok)
            return None

        nodeDefFilepath = 'meta/nodes.json'
        defData = json.loads(open(nodeDefFilepath, 'r').read())
        editorFilepath = self.bindingFile
        editorData = json.loads(open(editorFilepath, 'r').read())

        resultDict = editor_validate_and_export(defData, editorData, os.path.basename(editorFilepath).split('.')[0],
                                                resPath)

        return resultDict

    def onlineValidate(self, scriptJsonData, scriptName, resPath):
        nodeDefFilepath = 'meta/nodes.json'
        defData = json.loads(open(nodeDefFilepath, 'r').read())

        resultDict = editor_validate_and_export(defData, json.loads(json.dumps(scriptJsonData)),
                                                os.path.basename(scriptName).split('.')[0], resPath)
        results = resultDict['result']
        errors = resultDict['errors']

        # 存在错误
        if results is None:
            QMessageBox.information(None,
                                    'Info',
                                    scriptName + ' Validate Fail !!!',
                                    QMessageBox.Ok)
            return None
        return results

    def getScriptJsonData(self):
        controller = ControllerManager().getController(self.controllerKey)
        data = controller.getData()
        return data

    def getUUidIndex(self, scriptData):
        """得到节点的uuid和idx对应表"""
        uuididx = {}
        nodeData = scriptData['nodes']
        for node in nodeData:
            nodeUUID, nodeIDX = node['nodeUUidIdx']
            uuididx[nodeUUID] = nodeIDX
        return uuididx

    def get_level_list(self, level_config_data):
        level_list = {}
        for level_id in level_config_data:
            server_script_name = level_config_data[level_id].get('level_script', None)
            client_script_name = level_config_data[level_id].get('client_level_script', None)
            client_global_script_name = level_config_data[level_id].get('client_global_level_script', None)

            if server_script_name is not None:
                if server_script_name not in level_list:
                    level_list[server_script_name] = []
                level_list[server_script_name].append(level_id)

            if client_script_name is not None:
                if client_script_name not in level_list:
                    level_list[client_script_name] = []
                level_list[client_script_name].append(level_id)

            if client_global_script_name is not None:
                if client_global_script_name not in level_list:
                    level_list[client_global_script_name] = []
                level_list[client_global_script_name].append(level_id)

        return level_list

    def preRun(self, scriptName, scriptsData, resPath):
        scriptData = self.onlineValidate(scriptsData[scriptName]['data'], scriptName, resPath)
        if scriptData is None:
            return None
        UUidIdx = self.getUUidIndex(scriptData)
        scriptsData[scriptName]['scene'].isRun = True
        scriptsData[scriptName]['scene'].setUuidIdxMap(UUidIdx)
        return scriptData

    def runInGame(self, scriptsData, withTable=False):
        filename = '%s' % os.path.splitext(os.path.split(self.bindingFile)[-1])[0]

        from RPyCClient import RpycController
        r = RpycController()
        r.connect()
        r.execute('print " #####   pos 0   ######"')

        G = r.Base.GlobalRef.GlobalRef
        G.dataMgr.reset_temp_instance()

        level_config_data = eval(G.dataMgr.get_level_config())
        level_list = self.get_level_list(level_config_data)

        if filename not in level_list:
            QMessageBox.information(None,
                                    'Info',
                                    '找不到对应关卡!',
                                    QMessageBox.Ok)
            return
        else:
            if len(level_list[filename]) > 1:
                print(('find multiple levels, use first as default', level_list[filename]))
            level = level_list[filename][0]

        # how to get the prefs info elegantly
        prefs = self.parentWidget().parentWidget().parentWidget().parentWidget().prefs
        csv2pyPath = prefs['open_graph_dir'].replace('levelscripts', '')
        print(csv2pyPath)
        gameClientDir = prefs.get('game_client_dir', None)
        if not gameClientDir:
            filename = QFileDialog.getOpenFileName(self,
                                                   '选择client.exe文件，用于生成动画信息和本地路点信息',
                                                   '.',
                                                   'exe(*.exe)')
            if type(filename) == tuple:
                filename = str(filename[0])
            else:
                filename = str(filename)

            gameClientDir = os.path.dirname(filename)
            prefs['game_client_dir'] = gameClientDir
        if withTable:
            try:
                sys.path.append(os.path.join(csv2pyPath, 'SceneSocket'))
                socketTablePath = os.path.join(csv2pyPath, 'output/common/scene_socket.py')
                if os.path.exists(socketTablePath):
                    os.remove(socketTablePath)
                import ParseSceneSocket
                print(gameClientDir)
                os.system('svn up {}'.format(os.path.join(csv2pyPath, 'output')))
                ParseSceneSocket.parse_scene_socket(os.path.join(gameClientDir, 'res'),
                                                    os.path.join(csv2pyPath, 'output'))
                sceneSocketPath = os.path.join(csv2pyPath, 'output/common')
                print(('sceneSocketPath', sceneSocketPath))
                # r.loadModule('scene_socket', force=True, localPath=sceneSocketPath)
                import rpyc
                # it's strage that loadModule raise exception, errno 10054
                rpyc.utils.classic.upload(r.conn, os.path.join(csv2pyPath, 'output/common/scene_socket.py'),
                                          'script/tmp.py')
                r.execute("import sys\nif 'tmp' in sys.modules:del sys.modules['tmp']")
                r.execute(
                    "mod = __import__('tmp', fromlist=['']);from Base.GlobalRef import GlobalRef as G;G.dataMgr.datas['scene_socket'] = mod.data")
            except:
                traceback.print_exc()
                QMessageBox.information(None,
                                        'Info',
                                        '存在错误，本地导出路点功能失败，不会影响正常的调试功能，错误信息见日志。如果是svn up出错，请安装二进制版svn',
                                        QMessageBox.Ok)

        server_script_name = level_config_data[level]['level_script']
        client_script_name = level_config_data[level].get('client_level_script', None)
        client_global_script_name = level_config_data[level].get('client_global_level_script', None)
        resPath = os.path.join(gameClientDir, 'res')
        if server_script_name in scriptsData:
            server_data = self.preRun(server_script_name, scriptsData, resPath)
            if server_data is None:
                return
            G.dataMgr.get_level_from_editor_server(server_script_name, server_data)
        if client_script_name is not None and client_script_name in scriptsData:
            client_data = self.preRun(client_script_name, scriptsData, resPath)
            if client_data is None:
                return
            G.dataMgr.get_level_from_editor_client(client_script_name, client_data)
        if client_global_script_name is not None and client_global_script_name in scriptsData:
            client_global_data = self.preRun(client_global_script_name, scriptsData, resPath)
            if client_global_data is None:
                return
            G.dataMgr.get_level_from_editor_client(client_global_script_name, client_global_data)
        if client_global_script_name is None and 'global_empty_client' in scriptsData:
            client_global_data = self.preRun('global_empty_client', scriptsData, resPath)
            if client_global_data is None:
                return
            G.dataMgr.get_level_from_editor_client('global_empty_client', client_global_data)

        """退出副本"""
        if G.player:
            G.sceneMgr.clear()
            if G.world:
                temp = G.world
                G.world = None
                temp.destroy()
            G.playerController.destroy()
            G.playerController = None
            G.dialogMgr.clear()
            G.uiMgr.close_all(True, False)

        """进入关卡场景"""
        context = G
        context.logger.info("enter level=%d" % level)
        entityid = None

        if context.player:
            entityid = context.player.id
        data = {
            '_id': entityid,
            'id': entityid,
            'sceneid': level,
            'name': 'Test',
            'career': 1,
            'level': 1
        }
        player = context.playerMgr.create_or_init_player(data)
        player.set_standalone(True)
        if not context.player:
            player.on_become_player()

        player.update_external_table('scene_config', {'create_breakable': True})
        player.create_worldinstance(context, level)

        r.execute('print " #####   pos 1   ######"')
        #		r.onDisconnect()
        print('run in game succ')

    def shortFileName(self):
        if self.bindingFile is None:
            return None
        dirname = os.path.dirname(self.bindingFile)
        l = len(dirname)
        return self.bindingFile[l + 1:]

    def sceneEdited(self):
        self.updateEdit(True)

    def updateEdit(self, flag):
        self.editFlag = flag
        self.editStateChanged.emit()

    def closeWidget(self, scriptsData):
        if self.bindingFile is not None:
            scriptname = '%s' % os.path.splitext(os.path.split(self.bindingFile)[-1])[0]
            if scriptsData.get(scriptname, None):
                del scriptsData[scriptname]
        ControllerManager().removeController(self.controllerKey)
        self.blankWidget.timer.stop()

    def getNodesFromIndex(self, term, flag, vague):
        if flag == 1:
            nodes_tmp = self._searchContentInIndex(term, self.valueIndex, vague)
        elif flag == 2:
            nodes_tmp = self._searchContentInIndex(term, self.nameIndex, vague)
        else:
            nodes_tmp = self._searchContentInIndex(term, self.commentIndex, vague)
        return nodes_tmp

    def _searchContentInIndex(self, term, index, vague):
        nodes = set()
        if vague:
            nodes = self._vagueSearchInIndex(term, index)
        else:
            if term in index:
                nodes = index[term]
        return nodes

    def _vagueSearchInIndex(self, term, index):
        nodes_tmp = set()
        for key, value in list(index.items()):
            if term in key:
                nodes_tmp |= value
        return nodes_tmp

    def computeFindResult(self, content, searchFlag, vague=True):
        """
        计算查找结果
        vague 是否启用模糊搜索
        """
        self.findResult.clear()
        self.findResultItems = []
        textTerms = content.split()

        nodes_1 = self.allNodes
        nodes_2 = self.allNodes
        nodes_3 = self.allNodes
        for term in textTerms:
            nodes_tmp = self.getNodesFromIndex(term, 1, vague)
            nodes_1 = nodes_1 & nodes_tmp
        for term in textTerms:
            nodes_tmp = self.getNodesFromIndex(term, 2, vague)
            nodes_2 = nodes_2 & nodes_tmp
        for term in textTerms:
            nodes_tmp = self.getNodesFromIndex(term, 3, vague)
            nodes_3 = nodes_3 & nodes_tmp

        if searchFlag == 1:
            self.findResult = nodes_1
        elif searchFlag == 2:
            self.findResult = nodes_2
        elif searchFlag == 3:
            self.findResult = nodes_1 | nodes_2
        elif searchFlag == 4:
            self.findResult = nodes_3
        elif searchFlag == 5:
            self.findResult = nodes_1 | nodes_3
        elif searchFlag == 6:
            self.findResult = nodes_2 | nodes_3
        elif searchFlag == 7:
            self.findResult = nodes_1 | nodes_2 | nodes_3

        self.findResultItems = list(self.findResult)
        return self.findResultItems

    def highLightResult(self, curResultIndex):
        controller = ControllerManager().getController(self.controllerKey)
        self.targetNode = self.findResultItems[curResultIndex]
        self.prevNodeList = controller.getPrevNode(self.targetNode)
        self.nextNodeList = controller.getNextNode(self.targetNode)
        self.prevEdgeList = controller.getPrevEdge(self.targetNode)
        self.nextEdgeList = controller.getNextEdge(self.targetNode)

        self.scene.locateFind(self.targetNode)
        self.scene.locateFindNode(self.prevNodeList, self.nextNodeList)
        self.scene.locateFindEdge(self.prevEdgeList, self.nextEdgeList)
        print(('find at (%.1f, %.1f)' % (self.targetNode.x(), self.targetNode.y())))

    def highLightNode(self, node):
        # for replace
        controller = ControllerManager().getController(self.controllerKey)
        self.targetNode = node
        self.prevNodeList = controller.getPrevNode(self.targetNode)
        self.nextNodeList = controller.getNextNode(self.targetNode)
        self.prevEdgeList = controller.getPrevEdge(self.targetNode)
        self.nextEdgeList = controller.getNextEdge(self.targetNode)

        self.scene.locateFind(self.targetNode)
        self.scene.locateFindNode(self.prevNodeList, self.nextNodeList)
        self.scene.locateFindEdge(self.prevEdgeList, self.nextEdgeList)
        self.logger.info('find at (%.1f, %.1f)' % (self.targetNode.x(), self.targetNode.y()))

    def clearLastFind(self):
        self.scene.clearFind(self.targetNode, self.prevNodeList, self.nextNodeList, self.prevEdgeList,
                             self.nextEdgeList)
        self.targetNode = None
        self.prevNodeList = []
        self.nextNodeList = []
        self.prevEdgeList = []
        self.nextEdgeList = []

    def find_(self):
        print('in widget find')
        controller = ControllerManager().getController(self.controllerKey)
        if not self.nameIndex:
            self.nameIndex = controller.invertIndexByName()
            self.valueIndex = controller.invertIndexByValue()
            self.commentIndex = controller.invertIndexByComment()
            nodes = controller.nodes
            for node in nodes:
                self.allNodes.add(node)
        dlg = FindDialog(self)
        dlg.show()

    def endFind(self):
        print('end find')
        self.scene.clearFind(self.targetNode, self.prevNodeList, self.nextNodeList, self.prevEdgeList,
                             self.nextEdgeList)
        self.targetNode = None
        self.prevNodeList = []
        self.nextNodeList = []
        self.prevEdgeList = []
        self.nextEdgeList = []
        self.findResultItems = []

    def replace(self):
        self.logger.debug('Start Replacing')
        targetNodes = self.scene.getSelectedNodes()
        targetNodes = targetNodes if targetNodes else ControllerManager().getController(self.controllerKey).nodes
        dlg = ReplaceDialog(targetNodes, self)
        dlg.show()

    # raise NotImplementedError

    def getArgsNameInNode(self, nodeName):
        nodes = ControllerManager().itemData
        for node in nodes:
            if nodeName == node['name'][0]:
                return [arg['name'][0] for arg in node['args']]
        return []

    def findNodeByArgValue(self, nodeName, argName, searchValue, chosenNodes=None):
        # chosenNodes is used by replace in several selected nodes
        controller = ControllerManager().getController(self.controllerKey)
        return controller.findNodeByArgValue(nodeName, argName, searchValue, chosenNodes)

    def itemFold(self):
        self.scene.foldSelectedItems()

    def itemUnfold(self):
        self.scene.unfoldSelectedItems()

    def commentItem(self):
        self.scene.commentSelectedItems()

    def freeComment(self):
        self.scene.freeComment()

    def itemWider(self):
        self.scene.widerSelectedItems()

    def itemThinner(self):
        self.scene.thinnerSelectedItems()

    def deleteItem(self):
        self.scene.deleteSelectedItems()
        self.updateEdit(True)

    def copyItem(self):
        self.scene.copyItem()

    def cutItem(self):
        self.scene.cutItem()

    def pasteItem(self, mousePosition=None):
        self.scene.pasteItem(mousePosition)


class TemplateWidget(QWidget):
    """
    对每个node生成一个实例，作为编辑模板
    """
    editStateChanged = pyqtSignal()

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.sceneWidth = 10000
        self.sceneHeight = 10000
        self.bindingFile = 'meta/template.json'

        self.editFlag = False

        self.scene = TemplateScene()
        self.scene.showDynamicMenu = False
        self.scene.setSceneRect(QRectF(-self.sceneWidth / 2.0, -self.sceneHeight / 2.0,
                                       self.sceneWidth, self.sceneHeight))
        self.scene.itemSelected.connect(self.itemSelected)
        self.scene.editSignal.connect(self.sceneEdited)

        self.view = DiagramView(self.scene)
        # self.view.setBackgroundBrush(QColor(230, 200, 167))
        self.view.setBackgroundBrush(QColor(41, 41, 41))
        self.view.setMouseTracking(True)

        layout = QHBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

    def closeWidget(self):
        pass

    def itemSelected(self, item):
        pass

    def sceneEdited(self):
        self.updateEdit(True)

    def saveTemplate(self):
        self.scene.saveTemplate()
        self.updateEdit(False)

    def updateEdit(self, flag):
        self.editFlag = flag
        self.editStateChanged.emit()


class QuickDockWidget(QWidget):
    def __init__(self, parent=None):
        import copy
        super(self.__class__, self).__init__(parent)
        # self.foldButton = QPushButton(u'收起')
        # self.foldButton.clicked.connect(self.foldClicked)
        # self.arrowLabel = QLabel('<<')
        # self.arrowLabel.setStyleSheet('QLabel {color: gray}')
        # self.isFolded = False

        widgetBar = QWidget()
        widgetLayout = QHBoxLayout()
        self.initButtons(widgetLayout)
        widgetBar.setLayout(widgetLayout)
        # foldBar = QWidget()
        # foldLayout = QHBoxLayout()
        # foldLayout.addWidget(self.foldButton)
        # foldLayout.addWidget(self.arrowLabel)
        # foldBar.setLayout(foldLayout)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(widgetBar)
        # mainLayout.addWidget(foldBar)
        self.setLayout(mainLayout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh)
        self.timer.start(5000)

    def initButtons(self, parentLayout):
        self.bindingItems = ControllerManager().tracker.topItems(6)
        self.buttons = []
        for i in range(6):
            btn = QPushButton(self.bindingItems[i].typeName)
            btn.clicked.connect(partial(self.chooseWidgetClicked, i))
            self.buttons.append(btn)

        for btn in self.buttons:
            parentLayout.addWidget(btn)

    def chooseWidgetClicked(self, index):
        if index >= len(self.bindingItems):
            return

        graphWidget = self.parentWidget()
        graphWidget.scene.chooseInsertItem([self.bindingItems[index].typeName,
                                            self.bindingItems[index].typeId])

    def refresh(self):
        self.bindingItems = ControllerManager().tracker.topItems(6)
        for i in range(len(self.buttons)):
            self.buttons[i].setText(self.bindingItems[i].typeName)


class ArgsDockWidget(QWidget):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)

        self.args_tab = QTableWidget()

        self.args_tab.setColumnCount(2)
        self.args_tab.setHorizontalHeaderLabels(['Name', 'Value'])

        # default settings
        self.args_tab.setSelectionBehavior(QAbstractItemView.SelectRows)  # 单击选中一行
        # self.args_tab.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 表格内容只读
        self.args_tab.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一个目标

        self.args_tab.verticalHeader().setVisible(True)
        self.args_tab.horizontalHeader().setVisible(True)
        # self.args_tab.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.args_tab.horizontalHeader().setSectionsMovable(True)
        self.args_tab.horizontalHeader().setStretchLastSection(True)
        # self.args_tab.verticalHeader().setStretchLastSection(True)
        self.args_tab.resizeColumnsToContents()
        self.args_tab.resizeRowsToContents()

        sizegrip = QSizeGrip(self.args_tab)
        browser_layout = QHBoxLayout(self.args_tab)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        browser_layout.addWidget(sizegrip, 0, Qt.AlignRight | Qt.AlignBottom)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.args_tab.setStyleSheet("color: rgb(0, 170, 0);"
                                    "background-color: rgb(57, 57, 57);")
        self.args_tab.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.args_tab.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.args_tab)


class ReadDataThread(QThread):
    dataSignal = pyqtSignal([dict], [str])

    def __init__(self, pipe, parent=None):
        super().__init__(parent)

        self.parent_conn = pipe

    def run(self):
        while True:
            pipe_data = self.parent_conn.recv()
            if isinstance(pipe_data, dict):
                self.dataSignal[dict].emit(pipe_data)
            if isinstance(pipe_data, str) and pipe_data == 'finished':
                self.dataSignal[str].emit(pipe_data)

# def test():
#     pass
#
#
# if __name__ == '__main__':
#     test()
