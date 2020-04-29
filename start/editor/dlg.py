# coding:utf-8
import util
import logger
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import *


DialogLogger = logger.getLogger('Dialog')


class ResizeSceneDialog(QDialog):
    def __init__(self, width, height, doneResizeCallback, parent=None):
        super(ResizeSceneDialog, self).__init__(parent)
        self.width = width
        self.height = height
        self.doneResizeCallback = doneResizeCallback

        layout = QGridLayout()
        widthLabel = QLabel('width')
        heightLabel = QLabel('height')
        self.widthInput = QLineEdit('%d' % self.width)
        self.heightInput = QLineEdit('%d' % self.height)
        widthUnitLabel = QLabel('px')
        heightUnitLabel = QLabel('px')
        cancelButton = QPushButton('Cancel')
        cancelButton.clicked.connect(self.reject)
        okButton = QPushButton('OK')
        okButton.clicked.connect(self.accept)
        okButton.setDefault(True)

        layout.addWidget(widthLabel, 0, 0, 1, 1)
        layout.addWidget(self.widthInput, 0, 1, 1, 1)
        layout.addWidget(widthUnitLabel, 0, 2, 1, 1)
        layout.addWidget(heightLabel, 1, 0, 1, 1)
        layout.addWidget(self.heightInput, 1, 1, 1, 1)
        layout.addWidget(heightUnitLabel, 1, 2, 1, 1)
        layout.addWidget(cancelButton, 2, 0, 1, 1)
        layout.addWidget(okButton, 2, 1, 1, 1)

        self.setLayout(layout)

    def accept(self):
        newWidth = int(self.widthInput.text())
        newHeight = int(self.heightInput.text())

        self.width = newWidth if newWidth > 0 else self.width
        self.height = newHeight if newHeight > 0 else self.height
        self.doneResizeCallback(self.width, self.height)
        super(ResizeSceneDialog, self).accept()

    # def reject(self):
    #     super(ResizeSceneDialog, self).reject()


class ChangeValueDialog(QDialog):
    def __init__(self, title, contentType, contentValue,
                 doneChangeCallback, parent=None):
        super(ChangeValueDialog, self).__init__(parent)
        self.setWindowTitle(title)
        self.contentType = contentType
        self.contentValue = contentValue
        self.doneChangeCallback = doneChangeCallback

        typeLabel = QLabel('类型')
        typeInput = QLabel(contentType)
        origLabel = QLabel('原值')
        origInput = QLabel(str(contentValue))
        newLabel = QLabel('新值')
        if contentValue is None:
            self.newInput = QLineEdit('')
        else:
            self.newInput = QLineEdit(str(contentValue))
        cancelButton = QPushButton('取消')
        cancelButton.clicked.connect(self.cancelClicked)
        resetButton = QPushButton('重为默认值')
        resetButton.clicked.connect(self.resetClicked)
        delButton = QPushButton('删除值')
        delButton.clicked.connect(self.delClicked)
        okButton = QPushButton('确定')
        okButton.clicked.connect(self.okClicked)
        okButton.setDefault(True)

        layout = QGridLayout()
        # row column 占用行数，占用列数
        layout.addWidget(typeLabel, 0, 0, 1, 1)
        layout.addWidget(typeInput, 0, 1, 1, 1)
        layout.addWidget(origLabel, 1, 0, 1, 1)
        layout.addWidget(origInput, 1, 1, 1, 1)
        layout.addWidget(newLabel, 2, 0, 1, 1)
        layout.addWidget(self.newInput, 2, 1, 1, 1)
        layout.addWidget(resetButton, 3, 0, 1, 1)
        layout.addWidget(delButton, 3, 1, 1, 1)
        layout.addWidget(cancelButton, 4, 0, 1, 1)
        layout.addWidget(okButton, 4, 1, 1, 1)

        self.setLayout(layout)

    def okClicked(self):
        sig, value = self.parseValue()
        if not sig:
            QMessageBox.warning(None,
                                'Error',
                                '输入值解析错误',
                                QMessageBox.Ok)
            super(ChangeValueDialog, self).reject()
            return

        self.doneChangeCallback(value, mode='set')
        super(ChangeValueDialog, self).accept()

    def cancelClicked(self):
        super(ChangeValueDialog, self).reject()

    def resetClicked(self):
        self.doneChangeCallback(None, mode='reset')
        super(ChangeValueDialog, self).accept()

    def delClicked(self):
        self.doneChangeCallback(None, mode='del')
        super(ChangeValueDialog, self).accept()

    def parseValue(self):
        text = str(self.newInput.text())
        print('user input', text)

        return util.parseValue(self.contentType, text)


class SaveQuestionDialog(QDialog):
    def __init__(self, doneChoice=None, index=None, parent=None):
        super(SaveQuestionDialog, self).__init__(parent=parent)

        self.doneChoice = doneChoice
        self.index = index

        label = QLabel('Do you want to save changes or cancel close?')
        discardButton = QPushButton('Discard')
        discardButton.clicked.connect(self.discardClicked)
        cancelButton = QPushButton('Cancel')
        cancelButton.clicked.connect(self.cancelClicked)
        saveButton = QPushButton('Save')
        saveButton.clicked.connect(self.saveClicked)
        saveButton.setDefault(True)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 4)
        layout.addWidget(cancelButton, 1, 0, 1, 1)
        layout.addWidget(discardButton, 1, 2, 1, 1)
        layout.addWidget(saveButton, 1, 3, 1, 1)
        self.setLayout(layout)

    def discardClicked(self):
        if self.doneChoice is not None:
            if self.index is not None:
                self.doneChoice('Discard', self.index)
            else:
                self.doneChoice('Discard')
        super(SaveQuestionDialog, self).accept()

    def cancelClicked(self):
        if self.doneChoice is not None:
            self.doneChoice('Cancel')
        super(SaveQuestionDialog, self).reject()

    def saveClicked(self):
        if self.doneChoice is not None:
            if self.index is not None:
                self.doneChoice('Save', self.index)
            else:
                self.doneChoice('Save')
        super(SaveQuestionDialog, self).accept()


class OverrideDialog(QDialog):
    def __init__(self, parent=None):
        super(OverrideDialog, self).__init__(parent=parent)

        label = QLabel('您选择的文件已存在，是否覆盖')
        cancelButton = QPushButton('否')
        cancelButton.clicked.connect(self.reject)
        okButton = QPushButton('是')
        okButton.clicked.connect(self.accept)
        okButton.setDefault(True)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(cancelButton, 1, 0, 1, 1)
        layout.addWidget(okButton, 1, 1, 1, 1)
        self.setLayout(layout)

    def accept(self):
        super(OverrideDialog, self).accept()

    def reject(self):
        super(OverrideDialog, self).reject()


class ScriptModeDialog(QDialog):
    def __init__(self, parent=None):
        super(ScriptModeDialog, self).__init__(parent=parent)

        label = QLabel('Select Script Mode')
        okButton = QPushButton('OK')
        okButton.clicked.connect(self.accept)
        clientMode = QRadioButton('Client')
        serverMode = QRadioButton('Server')
        serverMode.setChecked(True)
        self.modeSelect = QButtonGroup()
        self.modeSelect.addButton(clientMode)
        self.modeSelect.addButton(serverMode)
        self.modeSelect.setExclusive(True)
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 3)
        layout.addWidget(clientMode, 1, 0, 1, 1)
        layout.addWidget(serverMode, 2, 0, 1, 1)
        layout.addWidget(okButton, 3, 0, 1, 1)
        self.setLayout(layout)
        self.exec_()

    def selectedMode(self):
        for mode in self.modeSelect.buttons():
            if mode.isChecked() == True:
                return str(mode.text()).lower()

    def accept(self):
        super(ScriptModeDialog, self).accept()

    def reject(self):
        super(ScriptModeDialog, self).reject()


class ErrorConsoleDialog(QDialog):
    def __init__(self, errors, locateError, parent=None):
        super(ErrorConsoleDialog, self).__init__(parent=parent)
        self.locateError = locateError

        self.errList = QListWidget()
        self.fillErrorMessage(errors)
        self.errList.currentRowChanged.connect(self.onListRowChanged)

        okButton = QPushButton('OK')
        okButton.clicked.connect(self.accept)

        layout = QGridLayout()
        layout.addWidget(self.errList, 0, 0, 4, 3)
        layout.addWidget(okButton, 4, 2, 1, 1)
        self.setLayout(layout)

    def fillErrorMessage(self, errors):
        errIcon = QIcon('images/error.png')
        succIcon = QIcon('images/correct.png')

        if errors is None:
            self.errList.addItem(QListWidgetItem(succIcon, 'success!'))
            return

        hasErrors = False
        self.idList = []

        # 处理TypeError
        typeErrors = errors.get('TypeErrors', [])
        if len(typeErrors) != 0:
            for typeError in typeErrors:
                self.errList.addItem(QListWidgetItem(errIcon,
                                                     '%s:%s' % ('TypeError', typeError['message'])))
                self.idList.append((typeError['id'],
                                    typeError['subItemId']))
            hasErrors = True

        # 处理NullValueError
        noneValErrors = errors.get('NullValueError', [])
        if len(noneValErrors) != 0:
            for noneValError in noneValErrors:
                self.errList.addItem(QListWidgetItem(errIcon,
                                                     '%s:%s' % ('NullValueError', noneValError['message'])))
                self.idList.append((noneValError['id'],
                                    noneValError['subItemId']))
            hasErrors = True

        unknownErrors = errors.get('UnknownErrors', [])
        if len(unknownErrors) != 0:
            for unknownError in unknownErrors:
                self.errList.addItem(QListWidgetItem(errIcon,
                                                     '%s:%s' % ('UnknownValueError', unknownError.message)))
                self.idList.append(('UnknowError', str(unknownError)))
            hasErrors = True

        if not hasErrors:
            self.errList.addItem(QListWidgetItem(succIcon, 'success!'))

    def accept(self):
        self.parentWidget().scene.clearError()
        super(ErrorConsoleDialog, self).accept()

    def reject(self):
        self.parentWidget().scene.clearError()
        super(ErrorConsoleDialog, self).reject()

    def onListRowChanged(self, cRow):
        if len(self.idList) == 0:
            return

        self.locateError(*(self.idList[cRow]))


class FindDialog(QDialog):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setWindowTitle('"内容"是精确搜索，否则是模糊搜索')
        searchLabel = QLabel('查找内容')
        self.searchInput = QLineEdit('')
        self.searchInput.textChanged.connect(self.instantSearch)

        typeLabel = QLabel('类型')
        # 查找选项
        self.searchbycommentOption = QCheckBox('按注释')
        self.searchbynameOption = QCheckBox('按名称')
        self.searchbyvalueOption = QCheckBox('按值')
        self.searchbycommentOption.setChecked(True)
        self.searchbynameOption.setChecked(True)
        self.searchbyvalueOption.setChecked(True)

        self.infoLabel = QLabel('')
        findNextButton = QPushButton('Find Next')
        findNextButton.clicked.connect(self.findNextClicked)
        findPrevButton = QPushButton('Find Prev')
        findPrevButton.clicked.connect(self.findPrevClicked)
        findNextButton.setDefault(True)

        self.findResultsList = QTableWidget()
        self.columnNum = 2

        # default settings
        self.findResultsList.setSelectionBehavior(QAbstractItemView.SelectRows)  # 单击选中一行
        self.findResultsList.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 表格内容只读
        self.findResultsList.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一个目标
        self.findResultsList.verticalHeader().setVisible(True)
        self.findResultsList.horizontalHeader().setVisible(True)
        self.findResultsList.resizeColumnsToContents()

        # Event
        self.findResultsList.itemClicked.connect(self.switchToCuritem)

        layout = QGridLayout()
        layout.addWidget(searchLabel, 0, 0, 1, 1)
        layout.addWidget(self.searchInput, 0, 1, 1, 3)
        layout.addWidget(typeLabel, 1, 0, 1, 1)
        layout.addWidget(self.searchbycommentOption, 1, 1, 1, 2)
        layout.addWidget(self.searchbynameOption, 2, 1, 1, 2)
        layout.addWidget(self.searchbyvalueOption, 3, 1, 1, 2)
        layout.addWidget(self.infoLabel, 2, 3, 1, 1)
        layout.addWidget(findPrevButton, 4, 2, 1, 1)
        layout.addWidget(findNextButton, 4, 3, 1, 1)
        layout.addWidget(self.findResultsList, 5, 0, 5, 5)
        self.setLayout(layout)

        self.resultNum = 0
        self.searchResult = []
        self.curResultIndex = -1
        self.prevResultIndex = -1

    def reject(self):
        self.parentWidget().endFind()
        super(self.__class__, self).reject()

    def searchType(self):
        searchFlag = 0
        commentChecked = 0
        nameChecked = 0
        valueChecked = 0
        if self.searchbycommentOption.isChecked() == True:
            commentChecked = 1
        if self.searchbynameOption.isChecked() == True:
            nameChecked = 1
        if self.searchbyvalueOption.isChecked() == True:
            valueChecked = 1
        searchFlag = 4 * commentChecked + 2 * nameChecked + valueChecked
        return searchFlag

    def instantSearch(self):
        text = str(self.searchInput.text()).lower()
        vague = True
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
            vague = False
        searchTp = self.searchType()
        self.parentWidget().clearLastFind()
        self.findResultsList.clearContents()
        self.findResultsList.setRowCount(0)
        self.infoLabel.setText('%d/%d' % (0, 0))
        if text == '' or searchTp == 0:
            return
        self.searchResult = self.parentWidget().computeFindResult(text, searchTp, vague)
        self.resultNum = len(self.searchResult)
        if self.resultNum == 0:
            self.curResultIndex = -1
            return
        else:
            self.showSearchResult()
            self.curResultIndex = 0
            self.parentWidget().highLightResult(self.curResultIndex)
            for j in range(self.columnNum):
                self.findResultsList.item(self.curResultIndex, j).setSelected(True)
            curItem = self.findResultsList.item(self.curResultIndex, 0)
            self.findResultsList.scrollToItem(curItem, QAbstractItemView.EnsureVisible)
            self.prevResultIndex = self.curResultIndex
            self.infoLabel.setText('%d/%d' % (self.curResultIndex + 1, self.resultNum))

    def switchToCuritem(self):
        self.curResultIndex = self.findResultsList.currentRow()
        self.parentWidget().clearLastFind()
        self.selectItem()
        self.infoLabel.setText('%d/%d' % (self.curResultIndex + 1, self.resultNum))

    def showSearchResult(self):
        # clear history
        self.findResultsList.clearContents()
        self.findResultsList.setColumnCount(self.columnNum)
        self.findResultsList.setRowCount(self.resultNum)
        self.findResultsList.setHorizontalHeaderLabels(['Name', 'Comment'])

        for i in range(self.resultNum):
            resultName = self.searchResult[i].itemType.typeName
            if self.searchResult[i].comment is None:
                resultComment = ''
            else:
                resultComment = str(self.searchResult[i].comment.toPlainText())
            self.findResultsList.setItem(i, 0, QTableWidgetItem(resultName))
            self.findResultsList.setItem(i, 1, QTableWidgetItem(resultComment))

    def selectItem(self):
        self.parentWidget().highLightResult(self.curResultIndex)
        for j in range(self.columnNum):
            self.findResultsList.item(self.prevResultIndex, j).setSelected(False)
        for j in range(self.columnNum):
            self.findResultsList.item(self.curResultIndex, j).setSelected(True)
        curItem = self.findResultsList.item(self.curResultIndex, 0)
        self.findResultsList.scrollToItem(curItem, QAbstractItemView.EnsureVisible)
        self.prevResultIndex = self.curResultIndex

    def findNextClicked(self):
        if self.resultNum == 0:
            return
        self.parentWidget().clearLastFind()
        self.curResultIndex = (self.curResultIndex + 1) % self.resultNum
        self.selectItem()
        self.infoLabel.setText('%d/%d' % (self.curResultIndex + 1, self.resultNum))

    def findPrevClicked(self):
        if self.resultNum == 0:
            return
        self.parentWidget().clearLastFind()
        self.curResultIndex = (self.curResultIndex - 1 + self.resultNum) % self.resultNum
        self.selectItem()
        self.infoLabel.setText('%d/%d' % (self.curResultIndex + 1, self.resultNum))


class ExtendedCombo(QComboBox):
    def __init__(self, parent=None):
        super(ExtendedCombo, self).__init__(parent)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)
        self.completer = QCompleter(self)

        # always show all completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.pFilterModel = QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

        self.completer.setPopup(self.view())

        self.setCompleter(self.completer)

        self.lineEdit().textEdited[str].connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.setTextIfCompleterIsClicked)

    def setModel(self, model):
        super(ExtendedCombo, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedCombo, self).setModelColumn(column)

    def view(self):
        return self.completer.popup()

    def index(self):
        return self.currentIndex()

    def setTextIfCompleterIsClicked(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)


class ReplaceDialog(QDialog):
    def __init__(self, nodes, parent=None):
        super(self.__class__, self).__init__(parent)
        self.targetNodes = nodes
        self.legalNodes = set()
        for node in nodes:
            self.legalNodes.add(node.itemType.typeName)
        self.legalNodes = list(self.legalNodes)
        self.satisfiedNodes = []
        self.resultNum = 0
        self.chosenNum = 0
        self.currentIndex = -1

        self.setWindowTitle('替换指定节点的参数内容')
        nodeLabel = QLabel('节点名称')
        self.nodeInput = ExtendedCombo()

        model = QStandardItemModel()
        for i, word in enumerate([''] + self.legalNodes):
            item = QStandardItem(word)
            model.setItem(i, 0, item)

        self.nodeInput.setModel(model)
        # self.nodeInput.setModelColumn(0)
        self.nodeInput.editTextChanged.connect(self.updateArgInput)

        argLable = QLabel('参数名称')
        self.argInput = QComboBox()

        searchLabel = QLabel('查找值')
        self.searchInput = QLineEdit()
        findButton = QPushButton('Find')
        # self.searchInput.editingFinished.connect(self.findNodesByArgsValue)
        findButton.clicked.connect(self.findNodesByArgsValue)

        replaceLable = QLabel('替换值')
        self.replaceInput = QLineEdit()
        self.replaceInput.textChanged.connect(self.updateReplaceValues)
        replaceButton = QPushButton('Replace')
        replaceButton.clicked.connect(self.replace)
        self.infoLabel = QLabel('')
        self.findResultsList = QTableWidget()
        self.columnNum = 3

        # default settings
        self.findResultsList.setSelectionBehavior(QAbstractItemView.SelectRows)  # 单击选中一行
        self.findResultsList.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 表格内容只读
        self.findResultsList.setSelectionMode(QAbstractItemView.SingleSelection)  # 只能选中一个目标
        self.findResultsList.verticalHeader().setVisible(True)
        self.findResultsList.horizontalHeader().setVisible(True)
        self.findResultsList.resizeColumnsToContents()
        self.findResultsList.horizontalHeader().setStretchLastSection(True)
        # self.findResultsList.setAlternatingRowColors(True)

        # Event
        self.findResultsList.itemClicked.connect(self.switchToCuritem)

        deselect = QPushButton('反选')
        deselect.clicked.connect(self.deselect)

        layout = QGridLayout()
        layout.addWidget(nodeLabel, 0, 0, 1, 1)
        layout.addWidget(self.nodeInput, 0, 1, 1, 3)
        layout.addWidget(argLable, 1, 0, 1, 1)
        layout.addWidget(self.argInput, 1, 1, 1, 3)
        layout.addWidget(searchLabel, 2, 0, 1, 1)
        layout.addWidget(self.searchInput, 2, 1, 1, 3)
        layout.addWidget(findButton, 3, 3, 1, 1)
        layout.addWidget(replaceLable, 4, 0, 1, 1)
        layout.addWidget(self.replaceInput, 4, 1, 1, 3)
        layout.addWidget(replaceButton, 5, 3, 1, 1)
        layout.addWidget(self.infoLabel, 6, 0, 1, 1)
        layout.addWidget(deselect, 6, 3, 1, 1)
        layout.addWidget(self.findResultsList, 7, 0, 5, 4)

        self.setLayout(layout)

    def updateArgInput(self, nodeName):
        self.argInput.clear()
        if nodeName and nodeName in self.legalNodes:
            argsName = self.parentWidget().getArgsNameInNode(nodeName)
            for item in argsName:
                self.argInput.addItem(item)

    def updateReplaceValues(self, replaceValue):
        for i in range(self.resultNum):
            originContent = self.findResultsList.item(i, 1).text()
            suc, replaceContent = util.parseValue(self.contentType,
                                                  originContent.replace(self.searchInput.text(), replaceValue))
            replaceContent = str(replaceContent) if suc else '非法(不会进行替换)'
            self.findResultsList.item(i, 2).setText(replaceContent)

    def findNodesByArgsValue(self):
        nodeName = self.nodeInput.itemText(self.nodeInput.currentIndex())
        searchValue = self.searchInput.text()
        argName = self.argInput.itemText(self.argInput.currentIndex())
        if not searchValue or not nodeName or not argName:
            self._reset()
        else:
            DialogLogger.info(
                'Find node in replacing, find info is {0}, {1}, {2}'.format(nodeName, argName, searchValue))
            self.satisfiedNodes = self.parentWidget().findNodeByArgValue(nodeName, argName, searchValue,
                                                                         self.targetNodes)
            DialogLogger.info('Find result is:{}'.format(self.satisfiedNodes))
            if not self.satisfiedNodes:
                self._reset()
            else:
                self.showSearchResult()
                self.parentWidget().highLightNode(self.satisfiedNodes[self.currentIndex])
                for j in range(1, self.columnNum):
                    self.findResultsList.item(self.currentIndex, j).setSelected(True)
                curItem = self.findResultsList.item(self.currentIndex, 0)
                self.findResultsList.scrollToItem(curItem, QAbstractItemView.EnsureVisible)

    def updateChosenNums(self, value):
        if value:
            self.chosenNum += 1
        else:
            self.chosenNum -= 1
        self.infoLabel.setText('%d/%d' % (self.chosenNum, self.resultNum))

    def deselect(self):
        for i in range(self.resultNum):
            item = self.findResultsList.cellWidget(i, 0)
            state = item.isChecked()
            item.setChecked(not state)

    def replace(self):
        DialogLogger.info('replace values')
        if not self.chosenNum:
            QMessageBox.warning(None,
                                'Warning',
                                '替换时没有选中任何内容',
                                QMessageBox.Ok)
            # super(ReplaceDialog, self).accept()
            return
        argName = self.argInput.itemText(self.argInput.currentIndex())
        searchValue = self.searchInput.text()
        replaceValue = self.replaceInput.text()
        for i in range(self.resultNum):
            checkBox = self.findResultsList.cellWidget(i, 0)
            if checkBox.isChecked():
                node = self.satisfiedNodes[i]
                inputItem = node.getInputItemByName(argName)
                if inputItem:
                    contentType, contentValue = inputItem.itemContent.contentType, inputItem.itemContent.contentValue
                    suc, value = util.parseValue(contentType, str(contentValue).replace(searchValue, replaceValue))
                    if suc:
                        inputItem.doneChangeContentValue(value, mode='set')

        self._reset()
        self.findNodesByArgsValue()

    def reject(self):
        self.parentWidget().endFind()
        super(self.__class__, self).reject()

    def showSearchResult(self):
        self.resultNum = len(self.satisfiedNodes)
        self.currentIndex = 0
        self.chosenNum = 0
        self.findResultsList.clearContents()
        self.findResultsList.setColumnCount(self.columnNum)
        self.findResultsList.setColumnWidth(0, 20)
        self.findResultsList.setRowCount(self.resultNum)
        self.findResultsList.setHorizontalHeaderLabels(['', '初始值', '替换值'])
        argName = self.argInput.itemText(self.argInput.currentIndex())
        searchValue = self.searchInput.text()
        replaceValue = self.replaceInput.text()
        for i in range(self.resultNum):
            self.contentType, originContent = self.satisfiedNodes[i].getArgsTypeAndValue(argName)
            originContent = str(originContent)
            replaceContent = originContent.replace(searchValue, replaceValue)
            suc, replaceContent = util.parseValue(self.contentType, replaceContent)
            replaceContent = str(replaceContent) if suc else '非法(不会进行替换)'
            # checkItem = QTableWidgetItem('')
            # checkItem.setFlags(Qt.ItemIsUserCheckable)
            # checkItem.setCheckable(True)
            checkItem = QCheckBox()
            checkItem.stateChanged.connect(self.updateChosenNums)
            self.findResultsList.setCellWidget(i, 0, checkItem)
            self.findResultsList.setItem(i, 1, QTableWidgetItem(originContent))
            self.findResultsList.setItem(i, 2, QTableWidgetItem(replaceContent))

    def switchToCuritem(self):
        self.preIndex = self.currentIndex
        self.currentIndex = self.findResultsList.currentRow()
        self.parentWidget().clearLastFind()
        self.selectItem()

    def selectItem(self):
        self.parentWidget().highLightNode(self.satisfiedNodes[self.currentIndex])
        for j in range(1, self.columnNum):
            self.findResultsList.item(self.preIndex, j).setSelected(False)
            self.findResultsList.item(self.currentIndex, j).setSelected(True)
        curItem = self.findResultsList.item(self.currentIndex, 0)
        self.findResultsList.scrollToItem(curItem, QAbstractItemView.EnsureVisible)

    def _reset(self):
        self.currentIndex = -1
        self.satisfiedNodes = []
        self.resultNum = 0
        self.findResultsList.clearContents()


class TemplateDialog(QDialog):
    """
    模板编辑对话框
    """

    def __init__(self, name, note, doneEditCallback, parent=None):
        super(self.__class__, self).__init__(parent)
        label = QLabel('说明 %s' % name)
        cautionLabel = QLabel('注意事项')
        # self.edit = QLineEdit(u'')
        if note is None:
            self.edit = QTextEdit('')
            self.cautionEdit = QTextEdit('')
        else:
            self.edit = QTextEdit(note[0])
            self.cautionEdit = QTextEdit(note[1])

        okBtn = QPushButton('确定')
        cancelBtn = QPushButton('取消')
        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.reject)
        okBtn.setDefault(True)
        layout = QGridLayout()
        layout.addWidget(label, 0, 0, 1, 1)
        layout.addWidget(self.edit, 1, 0, 1, 3)
        layout.addWidget(cautionLabel, 2, 0, 1, 1)
        layout.addWidget(self.cautionEdit, 3, 0, 1, 3)
        layout.addWidget(cancelBtn, 4, 1, 1, 1)
        layout.addWidget(okBtn, 4, 2, 1, 1)

        self.setLayout(layout)

        self.doneEditCallback = doneEditCallback

    def accept(self):
        text = str(self.edit.toPlainText())
        if text.strip() != '':
            note = [str(self.edit.toPlainText()),
                    str(self.cautionEdit.toPlainText())]
            self.doneEditCallback(note)

        super(self.__class__, self).accept()

    def reject(self):
        super(self.__class__, self).reject()
