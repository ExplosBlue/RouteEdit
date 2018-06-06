import PointWidget
import RouteWidget
import bossPathWidget
import SARC as SarcLib
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

class MainWindow(QtWidgets.QMainWindow):
    """
    Main RoutEdit window
    """

    def __init__(self):
        super().__init__(None)
        self.setWindowTitle('RouteEdit')
        self.setGeometry(500, 500, 1000, 500)
        self.initUi()

    def initUi(self):

        # setup menu bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        toolBar = self.addToolBar('File')

        toolBar.setMovable(False)

        self.openFile = QtWidgets.QAction(QtGui.QIcon('RouteEditData/icons/folder.png'), '&Open', self)
        self.saveFile = QtWidgets.QAction(QtGui.QIcon('RouteEditData/icons/save.png'), '&Save', self)

        self.openFile.setShortcut('Ctrl+O')
        self.saveFile.setShortcut('Ctrl+S')

        self.openFile.setStatusTip('Open a file')
        self.openFile.setStatusTip('Save Changes')

        self.openFile.triggered.connect(self.loadSarc)
        self.saveFile.triggered.connect(self.saveSarc)

        self.saveFile.setDisabled(True)

        fileMenu.addAction(self.openFile)
        fileMenu.addAction(self.saveFile)

        toolBar.addAction(self.openFile)
        toolBar.addSeparator()
        toolBar.addAction(self.saveFile)


    def loadSarc(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'SARC files (*.sarc)')[0]

        if fileName == '':
            return

        with open(fileName, 'rb') as fileObj:
            data = fileObj.read()

        arc = SarcLib.SARC_Archive(data)
        arc.load(data)

        self.editor = editorTabWidget(arc.contents)
        self.setCentralWidget(self.editor)

        self.saveFile.setDisabled(False)

        for file in arc.contents:
            print('Filename: ' + str(file.name), ' Contents: ' + str(file.data))


    def saveSarc(self):
        arcContents = self.editor.getDataFromWidgets()
        newArchive = SarcLib.SARC_Archive()

        for file in arcContents:
            newArchive.addFile(file)

        outFile = newArchive.save()

        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Open file', '', 'SARC files (*.sarc)')[0]

        with open(fileName, 'wb+') as f:
            f.write(outFile)
            f.close()


class editorTabWidget(QtWidgets.QTabWidget):
    def __init__(self, arc, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)

        #TODO Change this so each editor is only passed the files they need instead of the whole archive

        pointFiles = []
        routeFiles = []
        bossPathFiles = []

        for file in arc:
            if not str(file.name).find('point'):
                pointFiles.append(file)
            if not str(file.name).find('route'):
                routeFiles.append(file)
            if not str(file.name).find('worldIn') or not str(file.name).find('toCastle'):
                bossPathFiles.append(file)

        # Create the editor widgets
        self.pointEditor = PointWidget.pointEditorWidget(pointFiles)
        self.routeEditor = RouteWidget.routeEditorWidget(routeFiles)
        self.bossPathEditor = bossPathWidget.bossPathEditorWidget(bossPathFiles)
        self.addTab(self.pointEditor, 'Node Unlocks')
        self.addTab(self.routeEditor, 'Path Settings')
        self.addTab(self.bossPathEditor, 'Boss Path')


    def getDataFromWidgets(self):
        pointFiles = self.pointEditor.getArc()
        routeFiles = self.routeEditor.getArc()
        bossPathFiles = self.bossPathEditor.getArc()

        arc = pointFiles + routeFiles + bossPathFiles

        return arc

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
