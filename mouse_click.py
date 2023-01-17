from qgis.PyQt.QtGui import (QPixmap, QImage)
from qgis.PyQt.QtWidgets import (QGraphicsScene, QGraphicsView)
from qgis.PyQt.QtCore import (Qt, pyqtSignal, QCoreApplication, QFileInfo, QRectF)
from qgis.core import (QgsRectangle, QgsProject)
from qgis.gui import (QgsMapTool, QgsRubberBand, QgsMapCanvas)

import os.path


class MouseClick(QgsMapTool):
    afterLeftClick = pyqtSignal()
    afterRightClick = pyqtSignal()
    afterDoubleClick = pyqtSignal()

    def __init__(self, canvas, drawSelf):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.drawSelf = drawSelf
        self.drawSelf.rb = None
        self.imageViewDLG = None

    def canvasPressEvent(self, event):
        if event.button() == 1:
            # sigeal : keep photo viewer on top of other windows
            if self.imageViewDLG != None :
                self.imageViewDLG.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.drawSelf.refresh()

    # sigeal : display photo on click instead of double-click
    #def canvasDoubleClickEvent(self, event):
    def canvasReleaseEvent(self, event):
        layers = self.canvas.layers()
        p = self.toMapCoordinates(event.pos())
        w = self.canvas.mapUnitsPerPixel() * 10
        try:
            rect = QgsRectangle(p.x() - w, p.y() - w, p.x() + w, p.y() + w)
        except:
            return
        layersSelected = []
        for layer in layers:
            if layer.type():
                continue
            fields = [field.name().upper() for field in layer.fields()]
            if 'IMAGE' in fields:
                lRect = self.canvas.mapSettings().mapToLayerCoordinates(layer, rect)
                layer.selectByRect(lRect)
                selected_features = layer.selectedFeatures()
                if selected_features != []:
                    layersSelected.append(layer)
                    feature = selected_features[0]
                    self.drawSelf.featureIndex = feature.id()
                    activeLayerChanged =  not hasattr(self.drawSelf, 'layerActive') or (self.drawSelf.layerActive != layer)
                    self.drawSelf.layerActive = layer
                    self.drawSelf.fields = fields
                    self.drawSelf.maxlen = len(self.drawSelf.layerActive.name())
                    self.drawSelf.layerActiveName = layer.name()
                    self.drawSelf.iface.setActiveLayer(layer)
                    imgPath = list(self.drawSelf.images.values())[self.drawSelf.featureIndex-1].source
                    if imgPath:
                        self.drawSelf.getImage = QImage(imgPath)
                        if self.imageViewDLG is None or activeLayerChanged:
                            self.imageViewDLG = QGraphicsView()
                        self.showImage()
                    else:
                        self.iface.messageBar().pushCritical("Error", "No file path present")
            
    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Image', message)

    def showImage(self):
        scene = QGraphicsScene()
        self.imageViewDLG.setScene(scene)
        pixmap = QPixmap.fromImage(self.drawSelf.getImage)
        scene.addPixmap(pixmap)
        self.imageViewDLG.fitInView(scene.itemsBoundingRect(), Qt.KeepAspectRatio)
        self.imageViewDLG.show()

        # self.imageViewDLG.viewer.scene.addPixmap(pixmap)
        # self.imageViewDLG.viewer.setSceneRect(QRectF(pixmap.rect()))
        # self.imageViewDLG.viewer.resizeEvent([])
        # self.imageViewDLG.showNormal()