import re
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

class bossPathEditorWidget(QtWidgets.QWidget):
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
        self.BossPathEntries = bossPathEntryContainer()

        # Setup Scroll Area
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.BossPathEntries)

        # Setup file selector
        for file in self.arc:
            if not str(file.name).find('worldIn'):
                self.fileSelector.addItem(str(file.name)[7:-4])

        self.fileSelector.currentIndexChanged.connect(self.fileIndexChanged)

        # add widgets to layout
        self.layout.addWidget(self.fileSelector)
        self.layout.addWidget(self.scrollArea)

        # load initial file
        self.fileIndexChanged()

    def fileIndexChanged(self):

        # store the currently selected file's name
        self.selectedFile = self.fileSelector.currentText() + ".csv"

        # check if a file is already open
        if self.fileLoaded:
            # if a file is already open, store the changes made and close the file
            self.storeChanges()
            self.BossPathEntries.reset()
            self.loadDataFromFile()
        else:
            self.loadDataFromFile()


    def loadDataFromFile(self):

        files = []

        # load the data for the file the user selected
        for file in self.arc:
            if file.name == "worldIn" + self.selectedFile:
                files.append(file)

            elif file.name == "toCastle" + self.selectedFile:
                files.append(file)

        self.BossPathEntries.populate(files)

        self.fileLoaded = True
        self.currentLoadedFile = self.selectedFile


    def storeChanges(self):
        data = self.BossPathEntries.bossPathToArray()

        i = 0

        for entry in data:
            if str(entry) == "worldIn":
                for file in self.arc:
                    if str(file.name) == "worldIn" + self.currentLoadedFile:
                        d = str(data[i+1])
                        d = d.encode('shiftjis')
                        file.data = d

            elif str(entry) == "toCastle":
                for file in self.arc:
                    if str(file.name) == "toCastle" + self.currentLoadedFile:
                        d = str(data[i+1])
                        d = d.encode('shiftjis')
                        file.data = d

            i += 1

    def getArc(self):
        self.storeChanges()
        return self.arc

class bossPathEntryContainer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.worldInEntries = []
        self.toCastleEntries = []

    def populate(self, files):

        for file in files:
            if not str(file.name).find("worldIn"):
                data = file.data
                data = data.decode('shiftjis')
                worldIn = worldInEntry(data)
                self.layout.addWidget(worldIn)
                self.worldInEntries.append(worldIn)

            if not str(file.name).find("toCastle"):
                data = file.data
                data = data.decode('shiftjis')
                toCaslte = toCastleEntry(data)
                self.layout.addWidget(toCaslte)
                self.toCastleEntries.append(toCaslte)

    def bossPathToArray(self):
        temp = []

        if self.worldInEntries != []:
            for worldIn in self.worldInEntries:
                temp.append('worldIn')
                temp.append(worldIn.valuesToString())

        if self.toCastleEntries != []:
            for toCastle in self.toCastleEntries:
                temp.append('toCastle')
                temp.append(toCastle.valuesToString())

        return temp

    def reset(self):
        self.clearLayout(self.layout)
        self.worldInEntries = []
        self.toCastleEntries = []

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

class worldInEntry(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.entries = []

        worldInLabel = QtWidgets.QLabel("WorldIn")
        self.layout.addWidget(worldInLabel)

        addEntryBtn = QtWidgets.QPushButton("+")
        addEntryBtn.pressed.connect(self.addNewEntry)

        removeEntryBtn = QtWidgets.QPushButton("-")
        removeEntryBtn.pressed.connect(self.removeEntry)

        buttonLayout = QtWidgets.QVBoxLayout()
        buttonLayout.addWidget(addEntryBtn)
        buttonLayout.addWidget(removeEntryBtn)

        self.layout.addLayout(buttonLayout)

        data = str(data).split(',')

        for i in data:
            lineEdit = QtWidgets.QLineEdit(i)
            self.entries.append(lineEdit)
            self.layout.addWidget(lineEdit)

        self.setMaximumHeight(75)

        # set background colour
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor(249, 249, 249))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def valuesToString(self):
        temp = []

        for lineEdit in self.entries:
            temp.append(lineEdit.text())

        output = ','.join(temp)
        output.encode('shiftjis')

        return output

    def addNewEntry(self):
        lineEdit = QtWidgets.QLineEdit()
        self.entries.append(lineEdit)
        self.layout.addWidget(lineEdit)

    def removeEntry(self):
        if len(self.entries) >= 2:
            if self.entries[-1] is not None:
                self.entries[-1].deleteLater()
            self.entries = self.entries[:-1]

class toCastleEntry(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.entries = []

        toCastleLabel = QtWidgets.QLabel("toCastle")
        self.layout.addWidget(toCastleLabel)

        addEntryBtn = QtWidgets.QPushButton("+")
        addEntryBtn.pressed.connect(self.addNewEntry)

        removeEntryBtn = QtWidgets.QPushButton("-")
        removeEntryBtn.pressed.connect(self.removeEntry)

        buttonLayout = QtWidgets.QVBoxLayout()
        buttonLayout.addWidget(addEntryBtn)
        buttonLayout.addWidget(removeEntryBtn)

        self.layout.addLayout(buttonLayout)

        data = str(data).split(',')

        for i in data:
            lineEdit = QtWidgets.QLineEdit(i)
            self.entries.append(lineEdit)
            self.layout.addWidget(lineEdit)

        self.setMaximumHeight(75)

        # set background colour
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor(249, 249, 249))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def valuesToString(self):
        temp = []

        for lineEdit in self.entries:
            temp.append(lineEdit.text())

        output = ','.join(temp)
        output.encode('shiftjis')

        return output

    def addNewEntry(self):
        lineEdit = QtWidgets.QLineEdit()
        self.entries.append(lineEdit)
        self.layout.addWidget(lineEdit)

    def removeEntry(self):
        if len(self.entries) >= 2:
            if self.entries[-1] is not None:
                self.entries[-1].deleteLater()
            self.entries = self.entries[:-1]
