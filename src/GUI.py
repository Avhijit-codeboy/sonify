import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (QComboBox, QFileDialog, QLabel, QStatusBar, QWidget, QApplication, QMainWindow,
                             QSplitter, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QMenu, QMenuBar, QSizePolicy
                             )
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self, parent = None):
        super().__init__()
        self.InitGUI()
        self.show()

    def CreateImagePane(self):
        self.canvas = FigureCanvasQTAgg()

        self.canvasLayout = QVBoxLayout()
        self.canvas.setLayout(self.canvasLayout)

    def CreateDrawer(self):
        self.drawer = QWidget()
        self.drawerLayout = QGridLayout()
        self.traverseLabel = QLabel("Traversing")
        self.traverseComboBox = QComboBox()
        # self.drawerLayout.addWidget(QLabel("Drawer"))
        self.drawer.setLayout(self.drawerLayout)

        self.mapLabel = QLabel("Mapping")
        self.mapComboBox = QComboBox()

        self.drawerLayout.addWidget(self.traverseLabel, 0, 0)
        self.drawerLayout.addWidget(self.traverseComboBox, 0, 1)

        self.drawerLayout.addWidget(self.mapLabel, 1, 0)
        self.drawerLayout.addWidget(self.mapComboBox, 1, 1)

    def InitGUI(self):
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        self.InitMenubar()
        self.InitMainWidget()
        # self.InitStatusBar()

        self.setCentralWidget(self.mainWidget)

    def InitMenubar(self):
        self.menubar = QMenuBar()
        self.fileMenu = QMenu("&File")
        self.editMenu = QMenu("&Edit")
        self.aboutMenu = QMenu("&About")

        self.menubar.addMenu(self.fileMenu)
        self.menubar.addMenu(self.editMenu)
        self.menubar.addMenu(self.aboutMenu)

        # File Menu Buttons

        self.action_file_open = QAction(QIcon("icons/icon_open.png"), "Open", self)
        self.action_file_open.setShortcut("Ctrl+O")

        self.action_file_exit = QAction(QIcon("icons/icon_exit.png"), "Exit", self)

        self.action_file_open.triggered.connect(lambda: self.FileOpen(None))
        self.action_file_exit.triggered.connect(self.Exit)
        self.aboutMenu.triggered.connect(lambda: print("DD"))

        self.fileMenu.addAction(self.action_file_open)
        self.fileMenu.addAction(self.action_file_exit)

        # Edit Menu Buttons

        self.action_edit_prefs = QAction(QIcon("icons/icon_prefs.png"), "Preferences", self)

        self.editMenu.addAction(self.action_edit_prefs)
        self.setMenuBar(self.menubar)

    def InitStatusBar(self):
        self.statusbar = QStatusBar()
        self.statusbar_layout = QHBoxLayout()
        self.statusbar.setLayout(self.statusbar_layout)
        self.setStatusBar(self.statusbar)
        self.mainLayout.addWidget(self.statusbar)

        self.status_filename = QLabel("DD")
        self.statusbar_layout.addWidget(self.status_filename)

    def InitMainWidget(self):
        self.mainSplitter = QSplitter(orientation = Qt.Orientation.Horizontal)
        # self.mainSplitter.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

        self.CreateImagePane()
        self.CreateDrawer()

        self.mainSplitter.addWidget(self.drawer)
        self.mainSplitter.addWidget(self.canvas)
        self.mainLayout.addWidget(self.mainSplitter)

    def FileOpen(self, fileName = None):
        if fileName is not None:
            self.file = QFileDialog.getOpenFileName(self, "Open File", filter = "Image Files (*.jpg *.jpeg *.png *.tiff *.hdf5 *.fits)")

            # if self.file is not None:

    def Exit(self):
        # TODO: handle ask on save
        QCoreApplication.exit(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    app.exec()
