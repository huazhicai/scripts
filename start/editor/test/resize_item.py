import sys
import PyQt5
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

global view
global scaleLabel

def scaleScene(event):
    delta = 1.0015**event.angleDelta().y()
    view.scale(delta, delta)
    scaleLabel.setPlainText("scale: %.2f"%view.transform().m11())
    view.update()

class ItemFilter(PyQt5.QtWidgets.QGraphicsItem):
    def __init__(self, target):
        super(ItemFilter, self).__init__()
        self.target = target

    def boundingRect(self):
        return self.target.boundingRect()
    def paint(self, *args, **kwargs):
        pass

    def sceneEventFilter(self, watched, event):
        if watched != self.target:
            return False

        if event.type() == PyQt5.QtCore.QEvent.GraphicsSceneMouseMove:
            self.target.setPos(self.target.pos()+event.scenePos()-event.lastScenePos())
            event.setAccepted(True)
            return True

        return super(ItemFilter, self).sceneEventFilter(watched, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # create main widget
    w = QWidget()
    w.resize(800, 600)
    layout = QVBoxLayout()
    w.setLayout(layout)
    w.setWindowTitle('Example')
    w.show()
    # rescale view on mouse wheel, notice how when view.transform().m11() is not 1,
    # dragging the subwindow is not smooth on the first mouse move event
    w.wheelEvent = scaleScene

    # create scene and view
    scene = QGraphicsScene()
    scaleLabel = scene.addText("scale: 1")
    view = QGraphicsView(scene)
    layout.addWidget(view)
    view.show();

    button = QPushButton('dummy')
    proxy = scene.addWidget(button, Qt.Window)
    proxy.setFlag(PyQt5.QtWidgets.QGraphicsItem.ItemIgnoresTransformations)

    itemFilter = ItemFilter(proxy)
    scene.addItem(itemFilter)
    proxy.installSceneEventFilter(itemFilter)

    # start app
    sys.exit(app.exec_())