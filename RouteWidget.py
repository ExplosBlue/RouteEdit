import re
from PyQt5 import QtCore, QtWidgets, QtGui

Qt = QtCore.Qt


class RouteEditorWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        self.archiveContents = []
        self.fileLoaded = False
        self.currentLoadedFile = ""
        self.selectedFile = ""
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create Widgets
        self.fileSelector = QtWidgets.QComboBox()
        self.scrollArea = QtWidgets.QScrollArea()
        self.routeEntries = RouteEntryTable()
        self.addRowButton = QtWidgets.QPushButton()
        self.delRowButton = QtWidgets.QPushButton()

        # Add Icons
        self.addRowButton.setIcon(QtGui.QIcon('RouteEditData/icons/plus.png'))
        self.delRowButton.setIcon(QtGui.QIcon('RouteEditData/icons/minus.png'))

        # Default Widgets to disabled
        self.fileSelector.setDisabled(True)
        self.scrollArea.setDisabled(True)

        # Setup Scroll Area
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.routeEntries)

        # Setup Signals
        self.fileSelector.currentIndexChanged.connect(self.fileIndexChanged)
        self.addRowButton.pressed.connect(self.addRow)
        self.delRowButton.pressed.connect(self.delRow)

        # add widgets to layout
        hLayout = QtWidgets.QHBoxLayout()
        hLayout.addWidget(self.fileSelector, 1, Qt.AlignVCenter)
        hLayout.addWidget(self.addRowButton, 0, Qt.AlignVCenter)
        hLayout.addWidget(self.delRowButton, 0, Qt.AlignVCenter)

        self.layout.addLayout(hLayout)
        self.layout.addWidget(self.scrollArea)

    def loadData(self, archiveContents):
        self.archiveContents = archiveContents

        QtCore.QObject.blockSignals(self.fileSelector, True)

        # Add elements to file selector drop-down
        for file in self.archiveContents:
            self.fileSelector.addItem(str(file.name)[5:-4])

        QtCore.QObject.blockSignals(self.fileSelector, False)

        # Enable the Ui
        self.scrollArea.setDisabled(False)
        self.fileSelector.setDisabled(False)

        # load initial file
        self.fileIndexChanged()

    def closeData(self):
        self.archiveContents = []
        self.fileLoaded = False
        self.currentLoadedFile = ""
        self.selectedFile = ""

        self.routeEntries.clearTable()

        self.fileSelector.setDisabled(True)
        self.scrollArea.setDisabled(True)

        self.fileSelector.clear()

    def fileIndexChanged(self):
        # store the currently selected file's name
        self.selectedFile = "route" + self.fileSelector.currentText() + ".csv"

        # check if a file is already open
        if self.fileLoaded:
            # if a file is already open, store the changes made and close the file
            self.storeChanges()
            self.routeEntries.clearTable()
            self.loadDataFromFile()
        else:
            self.loadDataFromFile()

    def loadDataFromFile(self):

        dataArray = []

        # load the data for the file the user selected
        for file in self.archiveContents:
            if file.name == self.selectedFile:
                data = file.data
                data = data.decode('shiftjis')

                # split data by row
                rows = str(data).split()

                # split rows elements but don't break substrings
                for row in rows:
                    row = re.split(''',(?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', row)
                    dataArray.append(row)

                # create a route entry container
                self.routeEntries.populate(dataArray)

                self.fileLoaded = True
                self.currentLoadedFile = self.selectedFile

    def storeChanges(self):
        data = self.routeEntries.saveContents()
        data = data.encode('shiftjis')

        for file in self.archiveContents:
            if str(file.name) == self.currentLoadedFile:
                file.data = data

    def getArchiveContents(self):
        self.storeChanges()
        return self.archiveContents

    def addRow(self):
        self.routeEntries.addRow()

    def delRow(self):
        self.routeEntries.delRow()


class RouteEntryTable(QtWidgets.QTableWidget):
    def __init__(self):
        QtWidgets.QTableWidget.__init__(self)

        # Setup Table Properties
        self.setColumnCount(3)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Setup Header Bar
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Path"))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Action"))
        self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem("Sound"))

        # Hide Row Numbers
        self.verticalHeader().setVisible(False)

    def populate(self, dataArray):
        i = 0
        # Iterate through each entry in the data array
        while i < len(dataArray):
            pos = self.rowCount()
            # Create a row for each entry in the array
            self.insertRow(pos)
            # Populate the new row with the contents of that entry in the array
            self.setItem(pos, 0, QtWidgets.QTableWidgetItem(dataArray[i][0]))  # Path
            self.setCellWidget(pos, 1, ActionEditor(dataArray[i][1]))          # Action
            self.setCellWidget(pos, 2, SoundEffectsEditor(dataArray[i][2]))    # Sound
            i += 1

    def addRow(self):
        self.insertRow(self.currentRow()+1)

        # Initialise the row
        self.setItem(self.currentRow()+1, 0, QtWidgets.QTableWidgetItem())  # Path
        self.setCellWidget(self.currentRow()+1, 1, ActionEditor())          # Action
        self.setCellWidget(self.currentRow()+1, 2, SoundEffectsEditor())    # Sound

    def delRow(self):
        self.removeRow(self.currentRow())

    def saveContents(self):
        outData = []

        row = 0
        # Iterate through each row of the table
        while row < self.rowCount():
            col = 0
            rowData = []
            # Iterate through each column for the current row
            while col < 3:
                # Store the contents of the column
                if col == 0:
                    rowData.append(self.item(row, col).text())
                else:
                    rowData.append(self.cellWidget(row, col).getValue())
                col += 1
            # Store the contents of each row
            rowString = ','.join(rowData)
            outData.append(rowString)
            row += 1

        outString = "\r\n".join(outData)
        return outString

    def clearTable(self):
        while self.rowCount() > 0:
            self.removeRow(0)


class SoundEffectsEditor(QtWidgets.QComboBox):
    def __init__(self, data=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Create a dictionary to translate the sfx names from jp to english
        self.sfx = {}
        with open('RouteEditData/SoundEffects.txt', 'rt', encoding="utf-8-sig") as f:
            for line in f:
                (jp, eng) = line.split(':')
                eng = str(eng).strip('\n')
                self.sfx[jp] = eng

        # Add translated sound effect names to the combobox
        for jp, eng in self.sfx.items():
            self.addItem(eng)

        if data is not None:
            self.getIndexByName(data)

    def getIndexByName(self, data):
        for jp, eng in self.sfx.items():
            if not str(data).find(jp):
                self.setCurrentIndex(self.findText(eng))

    def getValue(self):
        for jp, eng in self.sfx.items():
            if not self.currentText().find(eng):
                return jp


class ActionEditor(QtWidgets.QComboBox):
    def __init__(self, data=None, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)

        # Create a dictionary to translate the action names from jp to english
        self.actions = {}
        with open('RouteEditData/Actions.txt', 'rt', encoding="utf-8-sig") as f:
            for line in f:
                (jp, eng) = line.split(':')
                eng = str(eng).strip('\n')
                self.actions[jp] = eng

        # Add translated action names to the combobox
        for jp, eng in self.actions.items():
            self.addItem(eng)

        if data is not None:
            self.getIndexByName(data)

    def getIndexByName(self, data):
        for jp, eng in self.actions.items():
            if not str(data).find(jp):
                self.setCurrentIndex(self.findText(eng))

    def getValue(self):
        for jp, eng in self.actions.items():
            if not self.currentText().find(eng):
                return jp
