import PointWidget
import RouteWidget
import BossPathWidget
import SarcLib
import sys
from PyQt5 import QtCore, QtWidgets, QtGui

Qt = QtCore.Qt


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('RouteEdit')
        self.setGeometry(500, 500, 1500, 750)

        self.saveFile = QtWidgets.QAction(QtGui.QIcon('RouteEditData/icons/save.png'), '&Save', self)
        self.saveAsFile = QtWidgets.QAction(QtGui.QIcon('RouteEditData/icons/saveAs.png'), '&Save As', self)
        self.openFile = QtWidgets.QAction(QtGui.QIcon('RouteEditData/icons/folder.png'), '&Open', self)
        self.closeFile = QtWidgets.QAction(QtGui.QIcon('RouteEditData/icons/close.png'), '&Close', self)

        self.editor = EditorTabWidget()

        self.initUi()

        self.currentFilePath = ''

    def initUi(self):

        self.editor.setDisabled(True)

        # setup menu bar
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        toolBar = self.addToolBar('File')

        toolBar.setMovable(False)

        self.openFile.setShortcut('Ctrl+O')
        self.saveFile.setShortcut('Ctrl+S')
        self.saveAsFile.setShortcut('Ctrl+Shift+S')
        self.closeFile.setShortcut('Ctrl+W')

        self.openFile.setStatusTip('Open a file')
        self.saveFile.setStatusTip('Save Changes')
        self.saveAsFile.setStatusTip('Save As')
        self.closeFile.setStatusTip('Close the current file')

        self.openFile.triggered.connect(self.loadSarc)
        self.saveFile.triggered.connect(self.saveSarc)
        self.saveAsFile.triggered.connect(self.saveSarcAs)
        self.closeFile.triggered.connect(self.closeSarc)

        self.saveFile.setDisabled(True)
        self.saveAsFile.setDisabled(True)
        self.closeFile.setDisabled(True)

        fileMenu.addAction(self.openFile)
        fileMenu.addAction(self.saveFile)
        fileMenu.addAction(self.saveAsFile)
        fileMenu.addAction(self.closeFile)

        toolBar.addAction(self.openFile)
        toolBar.addSeparator()
        toolBar.addAction(self.saveFile)
        toolBar.addAction(self.saveAsFile)
        toolBar.addSeparator()
        toolBar.addAction(self.closeFile)

        self.setCentralWidget(self.editor)

    def loadSarc(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '', 'SARC files (*.sarc)')[0]

        if fileName == '':
            return

        self.currentFilePath = fileName

        with open(fileName, 'rb') as fileObj:
            data = fileObj.read()

        archive = SarcLib.SARC_Archive(data)
        archive.load(data)

        self.editor.loadData(archive.contents)

        self.saveFile.setDisabled(False)
        self.saveAsFile.setDisabled(False)
        self.closeFile.setDisabled(False)
        self.editor.setDisabled(False)

    def saveSarc(self):
        arcContents = self.editor.getDataFromWidgets()
        newArchive = SarcLib.SARC_Archive(endianness='<')

        for file in arcContents:
            newArchive.addFile(file)

        outFile = newArchive.save()[0]

        with open(self.currentFilePath, 'wb+') as f:
            f.write(outFile)

    def saveSarcAs(self):
        arcContents = self.editor.getDataFromWidgets()
        newArchive = SarcLib.SARC_Archive(endianness='<')

        for file in arcContents:
            newArchive.addFile(file)

        outFile = newArchive.save()[0]

        fileName = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file', '', 'SARC files (*.sarc)')[0]

        if fileName == '':
            return

        with open(fileName, 'wb+') as f:
            f.write(outFile)

    def closeSarc(self):
        closeDialog = QtWidgets.QMessageBox
        ret = closeDialog.question(self, '', 'Close the current file?', closeDialog.Yes | closeDialog.No)

        if ret == closeDialog.Yes:
            self.editor.closeFile()
            self.editor.setDisabled(True)
            self.saveFile.setDisabled(True)
            self.saveAsFile.setDisabled(True)
            self.closeFile.setDisabled(True)

            self.currentFilePath = ''


class EditorTabWidget(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        QtWidgets.QTabWidget.__init__(self, parent)

        self.pointEditor = PointWidget.PointEditorWidget()
        self.routeEditor = RouteWidget.RouteEditorWidget()
        self.bossPathEditor = BossPathWidget.BossPathEditorWidget()
        self.addTab(self.pointEditor, 'Node Unlocks')
        self.addTab(self.routeEditor, 'Path Settings')
        self.addTab(self.bossPathEditor, 'Boss Path')

    def loadData(self, archiveContents):
        self.closeFile()

        pointFiles = []
        routeFiles = []
        bossPathFiles = []

        for file in archiveContents:
            if not str(file.name).find('point'):
                pointFiles.append(file)
            elif not str(file.name).find('route'):
                routeFiles.append(file)
            elif not str(file.name).find('worldIn') or not str(file.name).find('toCastle'):
                bossPathFiles.append(file)
            else:
                print('Unknown File')
                print(file.name)

        self.pointEditor.loadData(pointFiles)
        self.routeEditor.loadData(routeFiles)
        self.bossPathEditor.loadData(bossPathFiles)

    def closeFile(self):
        self.pointEditor.closeData()
        self.routeEditor.closeData()
        self.bossPathEditor.closeData()

    def getDataFromWidgets(self):
        pointFiles = self.pointEditor.getArchiveContents()
        routeFiles = self.routeEditor.getArchiveContents()
        bossPathFiles = self.bossPathEditor.getArchiveContents()

        archiveContents = pointFiles + routeFiles + bossPathFiles

        return archiveContents


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
