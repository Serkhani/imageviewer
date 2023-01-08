# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImageSearcher
                                 A QGIS plugin
 A pseudo-google lens image search
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-01-07
        git sha              : $Format:%H$
        copyright            : (C) 2023 by NA
        email                : dak.boniface@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog
# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .image_searcher_dockwidget import ImageSearcherDockWidget
import os.path


class ImageSearcher:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ImageSearcher_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Image Searcher')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'ImageSearcher')
        self.toolbar.setObjectName(u'ImageSearcher')

        #print "** INITIALIZING ImageSearcher"

        self.pluginIsActive = False
        self.dockwidget = None
        self.importFolderPath = None #path to import image files from
        self.importFilesList = None #list of imported image files
        self.isImporting = False #kept to keep track of the statep plugin


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
        return QCoreApplication.translate('ImageSearcher', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action


    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/image_searcher/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Search for objects in geo-tagged images'),
            callback=self.run,
            parent=self.iface.mainWindow())

    #--------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""

        #print "** CLOSING ImageSearcher"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        #print "** UNLOAD ImageSearcher"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Image Searcher'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def importFolder(self):
        """importFolder method imports all images in the folder"""
        self.importFolderPath = QFileDialog.getExistingDirectory(
        self.dockwidget, caption="Select import folder",
        #directory=os.path.expanduser("~")
        directory="C:\\Users\\LENOVO\\Desktop\\3months Vac\\Soko Aerial\\Building QGIS plugins with Python\\Images",
        )

    def importFile(self):
        """importFile method imports an image file or a group of image files"""
        self.importFilesList = QFileDialog.getOpenFileNames(
        self.dockwidget, caption="Select image(s)",
        directory="C:\\Users\\LENOVO\\Desktop\\3months Vac\\Soko Aerial\\Building QGIS plugins with Python\\Images",
        filter="Image (*.jpg)")

    
    def checkIsImporting(self):
        """This method is used to set visibility of objects depending on whether importation is taking place"""
        self.dockwidget.importingLabel.setVisible(self.isImporting)
        self.dockwidget.imageName.setVisible(self.isImporting)
        self.dockwidget.indProgressBar.setVisible(self.isImporting)
        self.dockwidget.graphicsView.setVisible(self.isImporting)
        self.dockwidget.overallImgProgress.setVisible(self.isImporting)
        self.dockwidget.overallProgressBar.setVisible(self.isImporting)
    
    #--------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            #print "** STARTING ImageSearcher"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = ImageSearcherDockWidget()
                self.dockwidget.folderPushButton.clicked.connect(self.importFolder)
                self.dockwidget.filePushButton.clicked.connect(self.importFile)
                self.checkIsImporting()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.dockwidget)
            self.dockwidget.show()
