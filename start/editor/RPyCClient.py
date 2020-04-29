# -*- coding: utf-8 -*- 
import rpyc
import os
import threading
import time
import codecs

# 因为有的模块需要import一些remote上本来没有的东西
# 例如两个模块都是在本地定义的,要一起加载到remote上
# 如果不先声明一下,import时会报错
Dependencies = {
    'InputController': ['WayPoint'],
    'WayPoint': ['InputController', 'Spectator'],
    'Spectator': [],
}


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


# 用来接收remote端rpyc请求的线程
class CustomBgServingThread(object):
    # 0代表响应对面的rpyc调用的间隔
    SERVE_INTERVAL = 0.0
    # 默认0.1
    SLEEP_INTERVAL = 0.001

    def __init__(self, conn, callback=None):
        self._conn = conn
        self._thread = threading.Thread(target=self._bg_server)
        self._thread.setDaemon(True)
        self._active = True
        self._callback = callback
        # print '##########'
        self._thread.start()

    def __del__(self):
        if self._active:
            self.stop()

    def _bg_server(self):
        try:
            while self._active:
                self._conn.serve(self.SERVE_INTERVAL)
                time.sleep(self.SLEEP_INTERVAL)
        except Exception:
            if self._active:
                if self._callback:
                    self._callback()
                else:
                    print('_bg_server')
                    raise

    def stop(self):
        assert self._active
        self._active = False
        self._thread.join()
        self._conn = None


@singleton
class RpycController(object):
    def __init__(self):
        self.conn = None
        self.bgsrv = None
        # 使用set避免重复
        self.loadedModule = set()
        self.disconnectCallback = None
        # self._debug = False
        self._shortcuts = {}

    @property
    def shortcuts(self):
        return self._shortcuts

    @shortcuts.setter
    def shortcuts(self, value):
        self._shortcuts = value.copy()

    def reset(self):
        self.loadedModule = set()

    # 按给定的host和port进行连接
    # 如果传入了callback
    # 会以连接结果为参数调用callback
    def connect(self, callback=None, host="localhost", port=18812):
        try:
            self.conn = rpyc.classic.connect(host, port)
            self.bgsrv = CustomBgServingThread(self.conn, self.onDisconnect)
        except:
            if callback:
                callback(False)
            return False
        if callback:
            callback(True)
            return True

    @property
    def connected(self):
        return self.conn and not self.conn.closed

    def registerOnDisconnect(self, callback):
        self.disconnectCallback = callback

    def onDisconnect(self):
        try:
            self.bgsrv.stop()
        except Exception as e:
            print('Stop bgsrv error in onDisconnect: ', e)
            print(e)
        finally:
            if self.disconnectCallback:
                self.disconnectCallback()

    # name可以是模块简写名，先查找简写名
    def findModule(self, name):
        if name in self._shortcuts:
            return eval(self._shortcuts[name])
        elif name in self.conn.modules:
            return self.conn.modules[name]
        else:
            # print 'No module named ', name
            return None

    # 这个重载的作用是可以更方便,更自然地访问remote module
    # 例如:self.com.data.cdata <=> self.findModule('com').data.cdata
    # 又如:r = RpycController()
    # r.com.data.cdata <=> r.findModule('com').data.cdata
    def __getattr__(self, key):
        if self.conn:
            return self.findModule(key)
        else:
            return None

    # 这两个重载的作用是可以更方便的访问remote的namespace
    # 例如:self['a'] <=> self.conn.namespace['a']
    def __getitem__(self, key):
        return self.conn.namespace[key]

    def __setitem__(self, key, value):
        self.conn.namespace[key] = value

    # 重载所有在Dependencies里的模块
    def reloadAllModules(self):
        self.reset()
        for moduleName in Dependencies:
            if self.findModule(moduleName):
                self.loadModule(moduleName)

    # 将一个local module的代码传输到remote后令其载入
    # 如果有content,就用content,否则尝试从localPath读取这个module
    # remoteFlag为True的话,就会在模块里定义_remote = True
    # 作用是可以以此区分这段代码是运行在remote还是local
    # 因为有的模块可能在本地也需要import一下,但是里面又import了remote的东西
    # 直接用的话会报错
    def loadModule(self, modulePath, force=False, content=None, localPath="remote", remoteFlag=True):
        # 既不在本地已经load过的module中，也不在远程module中，再load
        if not force and (modulePath in self.loadedModule or self.findModule(modulePath)):
            return
        module = self.ensureModulePath(modulePath)
        # 先import, 再执行代码
        # 这是为了处理循环import的情况
        print("Load Module %s" % modulePath)
        # 用set来使不管force与否均可用这句，set自动去重
        self.loadedModule.add(modulePath)
        # 先load依赖的了local module到remote
        for name in Dependencies.get(modulePath, []):
            self.loadModule(name)
        if content is not None:
            code = content
        else:
            path = os.path.join(localPath, modulePath + ".py")
            with codecs.open(path, encoding="utf-8") as myfile:
                code = myfile.read().encode("utf-8")
        if remoteFlag:
            module._remote = True
        self['_c'] = code
        self['_m'] = module
        # 如果直接exec的话,在traceback文件名会显示为'string',不好调试
        # 这样子处理后文件名会是'FAKE/com/data/cdata/achievement_data.py'
        path = '[FAKE]/%s' + modulePath + ".py"
        self.execute("exec compile(_c, r'%s', 'exec') in _m.__dict__" % path)
        # reload的时候不要reload这个模块
        # self.reload_mgr._origin_modules.add(modulePath)

    def ensureModulePath(self, modulePath):
        self.execute("import imp")
        self.execute("import sys")
        parentModule = None
        # 不用递归了，modulePath在远程module中即可
        # if modulePath.find(".") > 0:
        # parentPath, moduleName = modulePath.rsplit(".", 1)
        # parentModule = self.ensureModulePath(parentPath)
        # else:
        # moduleName = modulePath

        # 再次用findModule判断下是为了处理force的情况
        if not self.findModule(modulePath):
            module = self.imp.new_module(modulePath)
            self.sys.modules[modulePath] = module
            self.execute("import %s" % modulePath)
        else:
            module = self.findModule(modulePath)
        # if parentModule:
        # setattr(parentModule, moduleName, module)
        return module

    def eval(self, *args):
        return self.conn.eval(*args)

    def execute(self, *args):
        self.conn.execute(*args)

    # 将常用远程模块简写，方便在命令行debug
    def addShortcuts(self):
        shorcuts = {
            'tar': "self.Globals.gameSceneMgr.getEntity(self.Globals.playerEntity.targetId)",
            'gm': 'self.debug.gm_cmd.GMCMDS().execute'
        }
        self.shortcuts = shorcuts

    # 命令行debug用
    # 加上这两个方法后,再执行如下语句
    # r = RpycController()
    # r.connect()
    # sys.meta_path = [r]
    # 此时在本地的所有import语句都会import remote module
    # 比如:
    # 在local执行 import Globals，远程也自动执行import Globals，
    # 此时,在local可以直接执行: Globals.gameSceneMgr.xxxxx
    # 如果要恢复的话,执行 sys.meta_path = []
    def find_module(self, fullname, path=None):
        # print 'find_module'
        # print fullname, path
        # 不管import什么都返回自身
        return self

    def load_module(self, full_name):
        # print 'load_module',full_name
        if self.conn is None:
            self.conn = rpyc.classic.connect(self.host, self.port)
        # 改为从远程获取module full_name
        module = getattr(self.conn.modules, full_name, None)
        return module


if __name__ == "__main__":
    r = RpycController()
    r.connect()
    # 测试连接
    print(r.os.getcwd())
    # 测试加载本地模块到远程
    modulePath = 'local_module'
    r.loadModule(modulePath, force=False, content=None, localPath=".", remoteFlag=True)
    # 测试加载远程模块到本地
    import sys

    sys.meta_path = [r]
    print(r.local_module.VAR)
    import remote_module

    print(remote_module.VAR)

    r.onDisconnect()
