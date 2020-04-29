#节点编辑器

##安装要求
###（源码使用）请安装如下一些依赖库
	1. numpy
	如果已经安装python，使用 pip install numpy 安装。

	2. PySide和PyQt4
	PySide可以通过pip安装。
	PyQt4需要先安装Qt，再安装PyQt4

	3. 如果一个一个包安装比较麻烦，可以考虑使用Python发行版
	Anaconda，自带了numpy和PyQt4

### 二进制格式
在dist目录下，双击main.exe，启动本工具。

##使用说明

###插入节点
在画布中选择右键，找到要插入的项目类别，再找到想插入的项目，点击选中。在画布上想要插入的地方，再左键点击一次。

###连线
直接从一个输出节点开始拖动，连接到与之匹配的输入节点上，即可建立连接。
点击工具栏箭头按钮，找到一个item的输出节点，找到另一个item的输入，如果这两者类型匹配，就可以建立一条连接

###移动节点
点击节点的标题，节点会处于选中状态，拖动标题实现item的移动

###移动画布
在空白区域，按住鼠标中键，拖动，可以移动画布。

###缩放场景
按住Alt键，滚动鼠标滚轮，可以自由缩放绘制图形的大小。

###打开，关闭，保存，新建
在工具的File菜单中，可以对创建的图进行这些操作.

###调整画布
在编辑->调整画布大小中，可以调整画布的大小。如果所作的图形很大，可以使用此功能。

###编辑子item值
如果一个子item挂载的数据是可编辑的5中基本类型之一，可以双击这个子item，在弹出的对话框中设置相应的值。
该数值既可以显示在界面上，也可以在保存阶段保存到图形中，随后的打开本设置依然存在。

###导出图片
选择 File-> Export Image，可以将图片以png格式导出。后缀名称可以自动补齐

###Undo和Redo
可以在做图形时，记录相关的步骤，可以撤销和执行之前的操作。次数无限。


##更新nodes.json元信息文件注意事项

### 给老的levels文件增加自带meta信息

给levels文件附加最新的版本信息
python MetaCompatChecker.py -c attach_meta -d <LEVEL_DIR>


### 检查更改项

检查新生成的版本和老版本之间做了哪些修改
python MetaCompatChecker.py -c list -d <LEVEL_DIR>

如果有类型的变更，会生成一个type_change.py模板
在里面定义类型转换的函数，并将自定义函数写到json格式的回调函数字符串中

### 更新levels

python MetaCompatChecker.py -c upgrade -d <LEVEL_DIR>

会自动进行节点增删，属性增删除的更新

并利用type_change.py里定义的类型转换规则完成类型的转换。

如果type_change时，某些被更改类型的属性附带有边，会将对应的边删除。
同时，删除那些边会以如下格式，写入到type_change.log中
level_file_name, startNode name, startAttr name, startNode pos    --> endNode name, endAttr name, endNode pos

可以通过此log来检查那些节点收到了影响，并进行相应的替换。


## 修改值
修改值的过程类似于更新meta。区别在于，修改值需要一个 value_change.in 模板，这个模板已经有一根示例。

value_change.in 根元素是list，list中的每个entry标识你想修改的某个节点的某个属性，给出节点和属性的type id。同时在files中指定想修改的特定几个文件。

### 生成修改值的模块模板
python MetaCompatChecker.py -c list_value -d <LEVEL_DIR>
根据 value_change.in 计算生成模块模板 value_change.py 
生成所更改的属性的所有可能取值。参考这些可能取值，可以方便书写回调函数。

对每个修改项，完成回调函数后，

### 进行值的修改
python MetaCompatChecker.py -c value_change -d <LEVEL_DIR>
根据 value_change.py 将定义的替换执行。

