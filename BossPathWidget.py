from PyQt5 import QtCore, QtWidgets, QtGui

Qt = QtCore.Qt


class BossPathEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.archiveContents = []
        self.fileLoaded = False
        self.currentLoadedFile = ''
        self.selectedFile = ''
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create Widgets
        self.fileSelector = QtWidgets.QComboBox()
        self.scrollArea = QtWidgets.QScrollArea()
        self.BossPathEntries = BossPathEntryContainer()

        # Setup Scroll Area
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.BossPathEntries)

        # Default Widgets to disabled
        self.fileSelector.setDisabled(True)
        self.scrollArea.setDisabled(True)

        # Setup Signals
        self.fileSelector.currentIndexChanged.connect(self.fileIndexChanged)

        # add widgets to layout
        topLayout = QtWidgets.QHBoxLayout()
        topLayout.addWidget(self.fileSelector, 1, Qt.AlignVCenter)

        self.layout.addLayout(topLayout)
        self.layout.addWidget(self.scrollArea)

    def loadData(self, archiveContents):
        self.archiveContents = archiveContents

        QtCore.QObject.blockSignals(self.fileSelector, True)

        # Add elements to file selector drop-down
        for file in self.archiveContents:
            if not str(file.name).find('worldIn'):
                self.fileSelector.addItem(str(file.name)[7:-4])

        QtCore.QObject.blockSignals(self.fileSelector, False)

        # Enable the Ui
        self.scrollArea.setDisabled(False)
        self.fileSelector.setDisabled(False)

        # load initial file
        self.fileIndexChanged()

    def closeData(self):
        self.archiveContents = []
        self.fileLoaded = False
        self.currentLoadedFile = ''
        self.selectedFile = ''

        self.BossPathEntries.reset()

        self.fileSelector.setDisabled(True)
        self.scrollArea.setDisabled(True)

        self.fileSelector.clear()

    def fileIndexChanged(self):

        # store the currently selected file's name
        self.selectedFile = self.fileSelector.currentText() + '.csv'

        # check if a file is already open
        if self.fileLoaded:
            # if a file is already open, store the changes made and close the file
            self.storeChanges()
            self.BossPathEntries.reset()
            self.loadSelectedFile()
        else:
            self.loadSelectedFile()

    def loadSelectedFile(self):

        files = []

        # load the data for the file the user selected
        for file in self.archiveContents:
            if file.name == 'worldIn' + self.selectedFile:
                files.append(file)

            elif file.name == 'toCastle' + self.selectedFile:
                files.append(file)

        self.BossPathEntries.populate(files)

        self.fileLoaded = True
        self.currentLoadedFile = self.selectedFile

    def storeChanges(self):
        data = self.BossPathEntries.bossPathToArray()

        i = 0

        for entry in data:
            if str(entry) == 'worldIn':
                for file in self.archiveContents:
                    if str(file.name) == 'worldIn' + self.currentLoadedFile:
                        d = str(data[i + 1])
                        d = d.encode('shiftjis')
                        file.data = d

            elif str(entry) == 'toCastle':
                for file in self.archiveContents:
                    if str(file.name) == 'toCastle' + self.currentLoadedFile:
                        d = str(data[i + 1])
                        d = d.encode('shiftjis')
                        file.data = d

            i += 1

    def getArchiveContents(self):
        self.storeChanges()
        return self.archiveContents


class BossPathEntryContainer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.worldInEntries = []
        self.toCastleEntries = []

    def populate(self, files):

        for file in files:
            if not str(file.name).find('worldIn'):
                data = file.data
                data = data.decode('shiftjis')
                worldIn = BossPathEntry(data, "World Into")
                self.layout.addWidget(worldIn, 0, Qt.AlignTop)
                self.worldInEntries.append(worldIn)

            if not str(file.name).find('toCastle'):
                data = file.data
                data = data.decode('shiftjis')
                toCastle = BossPathEntry(data, "From Tower")
                self.layout.addWidget(toCastle, 0, Qt.AlignTop)
                self.toCastleEntries.append(toCastle)

        if not self.toCastleEntries:
            self.layout.insertStretch(1, 0)

    def bossPathToArray(self):
        temp = []

        if self.worldInEntries:
            for worldIn in self.worldInEntries:
                temp.append('worldIn')
                temp.append(worldIn.valuesToString())

        if self.toCastleEntries:
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


class BossPathEntry(QtWidgets.QFrame, QtWidgets.QWidget):
    def __init__(self, data, name, parent=None):
        QtWidgets.QFrame.__init__(self, parent=parent)
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.setFrameShape(QtWidgets.QFrame.StyledPanel)

        self.layout = QtWidgets.QVBoxLayout(self)
        headerLayout = QtWidgets.QHBoxLayout()

        self.entries = []

        nameLabel = QtWidgets.QLabel(name)
        headerLayout.addWidget(nameLabel)

        addEntryBtn = QtWidgets.QPushButton('Insert Node')
        addEntryBtn.setIcon(QtGui.QIcon('RouteEditData/icons/plus.png'))
        addEntryBtn.pressed.connect(self.addNewEntry)

        removeEntryBtn = QtWidgets.QPushButton('Remove Node')
        removeEntryBtn.setIcon(QtGui.QIcon('RouteEditData/icons/minus.png'))
        removeEntryBtn.pressed.connect(self.removeEntry)

        # buttonLayout = QtWidgets.QVBoxLayout()
        headerLayout.addWidget(addEntryBtn)
        headerLayout.addWidget(removeEntryBtn)

        self.layout.addLayout(headerLayout)

        data = str(data).split(',')

        for i in data:
            lineEdit = QtWidgets.QLineEdit(i)
            self.entries.append(lineEdit)
            self.layout.addWidget(lineEdit)

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
