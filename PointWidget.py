import re
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

class pointEditorWidget(QtWidgets.QWidget):
    def __init__(self, arc, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.arc = arc
        self.fileLoaded = False
        self.currentLoadedFile = ""
        self.selectedFile = ""
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create Widgets
        self.fileSelector = QtWidgets.QComboBox()
        self.scrollArea = QtWidgets.QScrollArea()
        self.pointEntries = pointEntryContainer()
        self.header = header()

        # Setup Scroll Area
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.pointEntries)

        # Setup file selector
        for file in self.arc:
            self.fileSelector.addItem(str(file.name)[5:-4])

        self.fileSelector.currentIndexChanged.connect(self.fileIndexChanged)

        # add widgets to layout
        self.layout.addWidget(self.fileSelector)
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.scrollArea)

        # load initial file
        self.fileIndexChanged()


    def fileIndexChanged(self):

        # store the currently selected file's name
        self.selectedFile = "point" + self.fileSelector.currentText() + ".csv"

        # check if a file is already open
        if self.fileLoaded:
            # if a file is already open, store the changes made and close the file
            self.storeChanges()
            self.pointEntries.reset()
            self.loadDataFromFile()
        else:
            self.loadDataFromFile()


    def loadDataFromFile(self):

        dataArray = []

        # load the data for the file the user selected
        for file in self.arc:
            if file.name == self.selectedFile:
                data = file.data
                data = data.decode('shiftjis')

                # split data by row
                rows = str(data).split()

                # split rows elements but don't break substrings
                for row in rows:
                    row = re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', row)
                    dataArray.append(row)

                # create a point entry container
                self.pointEntries.populate(dataArray)

                self.fileLoaded = True
                self.currentLoadedFile = self.selectedFile


    def storeChanges(self):
        data = self.pointEntries.pointsToString()
        data = data.encode('shiftjis')

        for file in self.arc:
            if str(file.name) == self.currentLoadedFile:
                file.data = data

    def getArc(self):
        self.storeChanges()
        return self.arc

class pointEntryContainer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.pointEntries = []

    def populate(self, dataArray):
        i = 0
        while i < len(dataArray):
            point = pointEntry(dataArray[i])
            self.layout.addWidget(point)
            self.pointEntries.append(point)
            i += 1

    def pointsToString(self):
        temp = []
        for point in self.pointEntries:
            temp.append(point.valuesToString())
        outString = "\r\n".join(temp)
        outString = outString + "\r\n"
        return outString

    def reset(self):
        self.clearLayout(self.layout)
        self.pointEntries = [] # f

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

class pointEntry(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.idLabel = QtWidgets.QLabel(data[0])
        self.nodeName = QtWidgets.QLineEdit(data[1])
        self.nodeFlag = QtWidgets.QLineEdit(data[2])
        self.nodeUnlocks = QtWidgets.QLineEdit(data[3])
        self.pathUnlocks = QtWidgets.QLineEdit(data[4])
        self.pipeDest = QtWidgets.QLineEdit(data[5])
        self.seNodeUnlocks = QtWidgets.QLineEdit(data[6])
        self.sePathUnlocks = QtWidgets.QLineEdit(data[7])
        self.unk1 = QtWidgets.QLineEdit(data[8])

        # if data[2] == 'stop':
        #     self.stopFlag.setChecked(True)

        self.setMaximumHeight(75)

        self.layout.addWidget(self.idLabel)
        self.layout.addWidget(self.nodeName)
        self.layout.addWidget(self.nodeFlag)
        self.layout.addWidget(self.nodeUnlocks)
        self.layout.addWidget(self.pathUnlocks)
        self.layout.addWidget(self.pipeDest)
        self.layout.addWidget(self.seNodeUnlocks)
        self.layout.addWidget(self.sePathUnlocks)
        self.layout.addWidget(self.unk1)

        # set background colour
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor(249, 249, 249))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def valuesToString(self):
        temp = []
        temp.append(self.idLabel.text())
        temp.append(self.nodeName.text())
        temp.append(self.nodeFlag.text())
        # if self.stopFlag.isChecked():
        #     temp.append('stop')
        # else:
        #     temp.append('')
        temp.append(self.nodeUnlocks.text())
        temp.append(self.pathUnlocks.text())
        temp.append(self.pipeDest.text())
        temp.append(self.seNodeUnlocks.text())
        temp.append(self.sePathUnlocks.text())
        temp.append(self.unk1.text())
        output = ','.join(temp)
        output.encode('shiftjis')

        return output

class header(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        idLabel = QtWidgets.QLabel('ID')
        nodeNameLabel = QtWidgets.QLabel('Node Name')
        stopFlagLabel = QtWidgets.QLabel('Stop Flag')
        nodeUnlocksLabel = QtWidgets.QLabel('Node Unlocks')
        pathUnlocksLabel = QtWidgets.QLabel('Path Unlocks')
        pipeDestLabel = QtWidgets.QLabel('Pipe Destination')
        seNodeUnlocksLabel = QtWidgets.QLabel('Secondary Node Unlocks')
        sePathUnlocksLabel = QtWidgets.QLabel('Secondary Path Unlocks')
        unk1Label = QtWidgets.QLabel('Unk1')

        self.setMaximumHeight(75)

        self.layout.addWidget(idLabel)
        self.layout.addWidget(nodeNameLabel)
        self.layout.addWidget(stopFlagLabel)
        self.layout.addWidget(nodeUnlocksLabel)
        self.layout.addWidget(pathUnlocksLabel)
        self.layout.addWidget(pipeDestLabel)
        self.layout.addWidget(seNodeUnlocksLabel)
        self.layout.addWidget(sePathUnlocksLabel)
        self.layout.addWidget(unk1Label)

        # set background colour
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor(249, 249, 249))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
