import re
from PyQt5 import QtCore, QtWidgets, QtGui

Qt = QtCore.Qt


class PointEditorWidget(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.archiveContents = []
        self.fileLoaded = False
        self.currentLoadedFile = ""
        self.selectedFile = ""
        self.layout = QtWidgets.QVBoxLayout(self)

        # Create Widgets
        self.fileSelector = QtWidgets.QComboBox()
        self.scrollArea = QtWidgets.QScrollArea()
        self.pointEntries = PointEntryTable()
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
        self.scrollArea.setWidget(self.pointEntries)

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

        self.pointEntries.clearTable()

        self.fileSelector.setDisabled(True)
        self.scrollArea.setDisabled(True)

        self.fileSelector.clear()

    def fileIndexChanged(self):
        # store the currently selected file's name
        self.selectedFile = "point" + self.fileSelector.currentText() + ".csv"

        # check if a file is already open
        if self.fileLoaded:
            # if a file is already open, store the changes made and close the file
            self.storeChanges()
            self.pointEntries.clearTable()
            self.loadSelectedFile()
        else:
            self.loadSelectedFile()

    def loadSelectedFile(self):

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

                # create a point entry container
                self.pointEntries.populate(dataArray)

                self.fileLoaded = True
                self.currentLoadedFile = self.selectedFile

    def storeChanges(self):
        data = self.pointEntries.saveContents()
        data = data.encode('shiftjis')

        for file in self.archiveContents:
            if str(file.name) == self.currentLoadedFile:
                file.data = data

    def getArchiveContents(self):
        self.storeChanges()
        return self.archiveContents

    def addRow(self):
        self.pointEntries.addRow()

    def delRow(self):
        self.pointEntries.delRow()


class PointEntryTable(QtWidgets.QTableWidget):
    def __init__(self):
        QtWidgets.QTableWidget.__init__(self)

        # Setup Table Properties
        self.setColumnCount(9)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # Setup Header Bar
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("ID"))
        self.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Node Name"))
        self.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem("Node Flag"))
        self.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem("Node Unlocks"))
        self.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem("Path Unlocks"))
        self.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem("Secret Node Flag"))
        self.setHorizontalHeaderItem(6, QtWidgets.QTableWidgetItem("Secret Node Unlocks"))
        self.setHorizontalHeaderItem(7, QtWidgets.QTableWidgetItem("Secret Path Unlocks"))
        self.setHorizontalHeaderItem(8, QtWidgets.QTableWidgetItem("Revealed Path Connections"))

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
            self.setItem(pos, 0, QtWidgets.QTableWidgetItem(dataArray[i][0]))  # ID
            self.setItem(pos, 1, QtWidgets.QTableWidgetItem(dataArray[i][1]))  # Node Name
            self.setItem(pos, 2, QtWidgets.QTableWidgetItem(dataArray[i][2]))  # Node Flag
            self.setItem(pos, 3, QtWidgets.QTableWidgetItem(dataArray[i][3]))  # Node Unlocks
            self.setItem(pos, 4, QtWidgets.QTableWidgetItem(dataArray[i][4]))  # Path Unlocks
            self.setItem(pos, 5, QtWidgets.QTableWidgetItem(dataArray[i][5]))  # Secret Node Flag
            self.setItem(pos, 6, QtWidgets.QTableWidgetItem(dataArray[i][6]))  # Secret Node Unlocks
            self.setItem(pos, 7, QtWidgets.QTableWidgetItem(dataArray[i][7]))  # Secret Path Unlocks
            self.setItem(pos, 8, QtWidgets.QTableWidgetItem(dataArray[i][8]))  # Revealed Path Connections
            i += 1

    def addRow(self):
        self.insertRow(self.currentRow() + 1)

        # Initialise the row
        self.setItem(self.currentRow() + 1, 0, QtWidgets.QTableWidgetItem())  # ID
        self.setItem(self.currentRow() + 1, 1, QtWidgets.QTableWidgetItem())  # Node Name
        self.setItem(self.currentRow() + 1, 2, QtWidgets.QTableWidgetItem())  # Node Flag
        self.setItem(self.currentRow() + 1, 3, QtWidgets.QTableWidgetItem())  # Node Unlocks
        self.setItem(self.currentRow() + 1, 4, QtWidgets.QTableWidgetItem())  # Path Unlocks
        self.setItem(self.currentRow() + 1, 5, QtWidgets.QTableWidgetItem())  # Secret Node Flag
        self.setItem(self.currentRow() + 1, 6, QtWidgets.QTableWidgetItem())  # Secret Node Unlocks
        self.setItem(self.currentRow() + 1, 7, QtWidgets.QTableWidgetItem())  # Secret Path Unlocks
        self.setItem(self.currentRow() + 1, 8, QtWidgets.QTableWidgetItem())  # Revealed Path Connections

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
            while col < 9:
                # Store the contents of the column
                rowData.append(self.item(row, col).text())
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
