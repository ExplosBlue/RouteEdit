import re
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

class routeEditorWidget(QtWidgets.QWidget):
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
        self.routeEntries = routeEntryContainer()
        self.header = header()

        # Setup Scroll Area
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.routeEntries)

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
        self.selectedFile = "route" + self.fileSelector.currentText() + ".csv"

        # check if a file is already open
        if self.fileLoaded:
            # if a file is already open, store the changes made and close the file
            self.storeChanges()
            self.routeEntries.reset()
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

                # create a route entry container
                self.routeEntries.populate(dataArray)

                self.fileLoaded = True
                self.currentLoadedFile = self.selectedFile


    def storeChanges(self):
        data = self.routeEntries.routesToString()
        data = data.encode('shiftjis')

        for file in self.arc:
            if str(file.name) == self.currentLoadedFile:
                file.data = data

    def getArc(self):
        self.storeChanges()
        return self.arc

class routeEntryContainer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.routeEntries = []

    def populate(self, dataArray):
        i = 0
        while i < len(dataArray):
            route = routeEntry(dataArray[i])
            self.layout.addWidget(route)
            self.routeEntries.append(route)
            i += 1

    def routesToString(self):
        temp = []
        for route in self.routeEntries:
            temp.append(route.valuesToString())
        outString = "\r\n".join(temp)
        outString = outString + "\r\n"
        return outString

    def reset(self):
        self.clearLayout(self.layout)
        self.routeEntries = [] # f

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                self.clearLayout(child.layout())

class routeEntry(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        self.pathName = QtWidgets.QLineEdit(data[0])
        self.movementType = QtWidgets.QLineEdit(data[1])
        self.soundEffect = QtWidgets.QLineEdit(data[2])

        self.setMaximumHeight(75)

        self.layout.addWidget(self.pathName)
        self.layout.addWidget(self.movementType)
        self.layout.addWidget(self.soundEffect)

        # set background colour
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor(249, 249, 249))
        self.setAutoFillBackground(True)
        self.setPalette(pal)

    def valuesToString(self):
        temp = []
        temp.append(self.pathName.text())
        temp.append(self.movementType.text())
        temp.append(self.soundEffect.text())
        output = ','.join(temp)
        output.encode('shiftjis')

        return output

class header(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent=parent)
        self.layout = QtWidgets.QHBoxLayout(self)

        pathName = QtWidgets.QLabel('Path')
        movementType = QtWidgets.QLabel('Movement Type')
        soundEffect = QtWidgets.QLabel('Sound Effect')

        self.setMaximumHeight(75)

        self.layout.addWidget(pathName)
        self.layout.addWidget(movementType)
        self.layout.addWidget(soundEffect)

        # set background colour
        pal = QtGui.QPalette()
        pal.setColor(QtGui.QPalette.Background, QtGui.QColor(249, 249, 249))
        self.setAutoFillBackground(True)
        self.setPalette(pal)
