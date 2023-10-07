import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt6 import QtWidgets
from PyQt6.QtCore import (QCoreApplication, QDir, QObject, Qt, 
                          QFileInfo, pyqtSignal as Signal, pyqtSlot as Slot)

from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (QComboBox, QFileDialog, QLabel, QPushButton, QStatusBar,
                             QWidget, QApplication, QMainWindow,
                             QSplitter, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QMenu, QMenuBar, QSizePolicy, QProgressBar,
                             )
from PyQt6.QtCore import QThread
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PIL import Image
import numpy as np
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename
import pandas as pd
import scipy as sp
import cv2
import sounddevice as sd
import time

import resources

# Global Variables
IMAGE_DIR = "images/"

class PlayAudio(QThread):
    def __init__(self, audio):
        super().__init__()
        self.audio = audio

    def run(self):
        print("DD")
        sd.play(self.audio)
        time.sleep(len(self.audio) * 0.1)
        sd.stop()

# Main Window class
class MainWindow(QMainWindow):
    music_signal = Signal(int)

    def __init__(self, parent = None):
        super().__init__()
        self.InitGUI()
        self.show()

    # Function for creating the image pane
    def CreateImagePane(self):
        self.InitCanvas()
        self.canvasLayout = QVBoxLayout()
        self.canvas.setLayout(self.canvasLayout)

    # Function for creating the drawer
    def CreateDrawer(self):

        # Drawer Widget
        self.drawer = QWidget()

        self.drawerLayout = QGridLayout()
        self.traverseLabel = QLabel("Traversing")
        self.traverseLabel.setToolTip("Method of moving through the image")

        # Travers Combo Box
        self.traverseComboBox = QComboBox()

        self.traverseComboBox.addItem("Left to Right")
        self.traverseComboBox.addItem("Right to Left")
        self.traverseComboBox.addItem("Top to Down")
        self.traverseComboBox.addItem("Down to Top")
        self.traverseComboBox.addItem("Top Down Stacked")
        self.traverseComboBox.addItem("Bottom Up Stacked")

        # self.drawerLayout.addWidget(QLabel("Drawer"))
        self.drawer.setLayout(self.drawerLayout)

        # Map Label
        self.mapLabel = QLabel("Mapping")
        self.mapLabel.setToolTip("Method of mapping the feature of image to parameters of sound")

        # Map Combo Box
        self.mapComboBox = QComboBox()
        self.mapComboBox.addItem("Color to Frequency")

        # Sample Rate Combo Box
        self.sampleRateLabel = QLabel("Sample Rate")
        self.sampleRateComboBox = QComboBox()

        self.sampleRateComboBox.addItems(["22050 Hz", "44100 Hz"])
            
        # Sonify Button

        self.sonifyButton = QPushButton(QIcon(":/icons/sonify.png"), "")

        self.sonifyButton.setToolTip("Sonify")
        self.sonifyButton.setDisabled(True)
        self.sonifyButton.clicked.connect(self.Sonify)

        # Play Button
        self.playButton = QPushButton(QIcon(":/icons/play.png"), "")
        self.playButton.setToolTip("Play")
        self.playButton.setEnabled(False)
        self.playButton.clicked.connect(self.Play)

        # Drawer Layout
        self.drawerLayout.addWidget(self.traverseLabel, 0, 0)
        self.drawerLayout.addWidget(self.traverseComboBox, 0, 1)
        self.drawerLayout.addWidget(self.mapLabel, 1, 0)
        self.drawerLayout.addWidget(self.mapComboBox, 1, 1)
        self.drawerLayout.addWidget(self.sampleRateLabel, 2, 0)
        self.drawerLayout.addWidget(self.sampleRateComboBox, 2, 1)
        self.drawerLayout.addWidget(self.sonifyButton, 4, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.drawerLayout.addWidget(self.playButton, 4, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)

        # Drawer Max Width
        self.drawer.setMaximumWidth(300)
    
    # Exit Function
    def Exit(self):
        # TODO: handle ask on save
        QCoreApplication.exit(0)

    # Function to handle opening files
    def FileOpen(self, fileName = None):
        if fileName is None:
            self.file = QFileDialog.getOpenFileName(self, "Open File",
                                                    filter = "Image Files (*.jpg *.jpeg *.png *.tiff *.hdf5 *.fits)")[0]
            if self.file == "":
                self.Msg("Please select an image", 10)
                return
        else:
            self.file = fileName
        
        self.Msg("Loading Image", 2)
        self.ReadImage()
        self.Msg("Image Loaded", 5)

    def FileSize(self):
        return str(QFileInfo(self.file).size())

    def Hue2freq(self, h,scale_freqs):
        thresholds = [26 , 52 , 78 , 104,  128 , 154 , 180]
        note = scale_freqs[0]
        if (h <= thresholds[0]):
            note = scale_freqs[0]
        elif (h > thresholds[0]) & (h <= thresholds[1]):
            note = scale_freqs[1]
        elif (h > thresholds[1]) & (h <= thresholds[2]):
            note = scale_freqs[2]
        elif (h > thresholds[2]) & (h <= thresholds[3]):
            note = scale_freqs[3]
        elif (h > thresholds[3]) & (h <= thresholds[4]):    
            note = scale_freqs[4]
        elif (h > thresholds[4]) & (h <= thresholds[5]):
            note = scale_freqs[5]
        elif (h > thresholds[5]) & (h <= thresholds[6]):
            note = scale_freqs[6]
        else:
            note = scale_freqs[0]
        return note

    # Initialisation function for the GUI
    def InitGUI(self):
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)

        self.InitMenubar()
        self.InitMainWidget()
        self.InitStatusBar()

        self.setCentralWidget(self.mainWidget)

    # Initialisation function for the canvas
    def InitCanvas(self):
        self.figure = Figure(figsize=(10, 10))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.subplots()
        self.ax.set_axis_off()

    # Initialisation function for the menubar
    def InitMenubar(self):
        self.menubar = QMenuBar()
        self.fileMenu = QMenu("&File")
        self.editMenu = QMenu("&Edit")
        self.viewMenu = QMenu("&View")
        self.aboutMenu = QMenu("&About")

        self.menubar.addMenu(self.fileMenu)
        self.menubar.addMenu(self.editMenu)
        self.menubar.addMenu(self.viewMenu)
        self.menubar.addMenu(self.aboutMenu)

        # File Menu Buttons

        self.action_file_open = QAction(QIcon(":/icons/open.png"), "Open", self)
        self.action_file_open.setShortcut("Ctrl+O")

        self.action_file_exit = QAction(QIcon(":/icons/exit.png"), "Exit", self)

        self.action_file_open.triggered.connect(lambda: self.FileOpen(None))
        self.action_file_exit.triggered.connect(self.Exit)

        self.fileMenu.addAction(self.action_file_open)
        self.fileMenu.addAction(self.action_file_exit)

        # Edit Menu Buttons

        self.action_edit_prefs = QAction(QIcon(":icons/prefs.png"), "Preferences", self)

        self.editMenu.addAction(self.action_edit_prefs)


        # View Menu Buttons

        self.action_view_overlay = QMenu("Overlay", self)
        
        self.action_view_overlay_line = QAction("Line", self)
        self.action_view_overlay_line.setChecked(True)
        self.action_view_overlay_line.setCheckable(True)

        self.action_view_overlay_sound_graph = QAction("Sound Graph", self)
        self.action_view_overlay_sound_graph.setChecked(True)
        self.action_view_overlay_sound_graph.setCheckable(True)

        self.action_view_overlay.addAction(self.action_view_overlay_line)
        self.action_view_overlay.addAction(self.action_view_overlay_sound_graph)

    
        self.viewMenu.addMenu(self.action_view_overlay)

        self.setMenuBar(self.menubar)

    # Initialisation function for the statusbar
    def InitStatusBar(self):
        self.statusbar = QStatusBar()
        self.statusbar_layout = QHBoxLayout()
        self.setStatusBar(self.statusbar)
        self.mainLayout.addWidget(self.statusbar)

        self.statusbar.setMaximumHeight(20)

        self.status_fileName = QLabel("File Name")
        self.status_fileSize = QLabel("File Size")
        self.status_fileDim = QLabel("File Dimension")
        self.statusbar.addPermanentWidget(self.status_fileName, 0)
        self.statusbar.addPermanentWidget(self.status_fileSize, 0)
        self.statusbar.addPermanentWidget(self.status_fileDim, 0)

        self.Msg("Hello World....", 5)

    # Initialisation function for the main widget
    def InitMainWidget(self):
        self.mainSplitter = QSplitter(orientation = Qt.Orientation.Horizontal)
        # self.mainSplitter.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

        self.CreateImagePane()
        self.CreateDrawer()

        self.mainSplitter.addWidget(self.drawer)
        self.mainSplitter.addWidget(self.canvas)
        self.mainLayout.addWidget(self.mainSplitter)

    #Function that handles the play button click
    def Play(self):
        self.worker = PlayAudio(self.song)
        self.worker.start()

        #self.worker.progress.connect(self.updateMusic)
        # self.worker.finished.connect(self.audioFinished)

    # Function for reading the image
    def ReadImage(self):
        self.img = Image.open(self.file)
        self.imghsv = cv2.cvtColor(np.array(self.img), cv2.COLOR_BGR2HSV)
        # self.ax.imshow(self.imghsv)
        self.ax.imshow(self.img)
        self.UpdateCanvas()

        # Update the statusbar info
        self.status_fileName.setText(self.file)
        self.status_fileSize.setText(self.FileSize())
        self.status_fileDim.setText(str(self.imghsv.shape))
        self.sonifyButton.setEnabled(True)

    # Function that handles the sonification
    def Sonify(self):
        self.progressbar_sonify = QProgressBar()
        self.statusbar.addPermanentWidget(self.progressbar_sonify)

        self.hues = []
        self.img_height, self.img_width, self.img_nlayers = self.imghsv.shape

        self.MapHorizontal_LR(5, 5)

        self.hues = pd.DataFrame(self.hues, columns= ["hues"])

        #Define frequencies that make up A-Harmonic Minor Scale
        scale_freqs = [220.00, 246.94 ,261.63, 293.66, 329.63, 349.23, 415.30] 

        self.hues['notes'] = self.hues.apply(lambda row : self.Hue2freq(row['hues'],scale_freqs), axis = 1)

        frequencies = self.hues['notes'].to_numpy()

        self.song = np.array([])

        self.SAMPLE_RATE = 22050

        T = 0.1

        self.t = np.linspace(0, T, int(T * self.SAMPLE_RATE), endpoint = False)

        # npixels = 100

        amp = 0.5

        for i in range(len(frequencies)):
            self.progressbar_sonify.setValue(int(100 % (i + 1)))
            val = frequencies[i]
            note = amp * np.sin(2 * np.pi * val * self.t)
            self.song = np.concatenate([self.song, note])

        self.playButton.setEnabled(True)

    # Helper function for showing message in the statusbar
    def Msg(self, msg = None, t = 1):
        self.statusbar.showMessage(msg, t * 1000)

    # Helper function to update canvas
    def UpdateCanvas(self):
        self.canvas.draw()

    # def map_stack(self, skipw, skiph):
    #     for i in range(0, self.img_height, int(self.img_height / skiph)):
    #         for j in range(0, self.img_width, int(self.img_width / skipw)):
    #             hue = imghsv[i][j][0] # Take H value
    #             self.hues.append(hue)

    def MapHorizontal_LR(self, skipw, skiph):
        for j in range(0, self.img_width, int(skipw % self.img_width)):
            for i in range(0, self.img_height, int(skiph % self.img_height)):
                hue = self.imghsv[i][j][0]
                self.hues.append(hue)
        print(self.hues)

    # def map_vertical(self, skipw = self.img_width, skiph = self.img_height):
    #     for j in range(1, self.img_width, int(self.img_width / skipw)):
    #         for i in range(0, self.img_height, int(self.img_height /  skiph)):
    #             hue = imghsv[i][j][0]
    #             self.hues.append(hue)

    def Get_piano_notes(self):   
        # White keys are in Uppercase and black keys (sharps) are in lowercase
        octave = ['C', 'c', 'D', 'd', 'E', 'F', 'f', 'G', 'g', 'A', 'a', 'B'] 
        base_freq = 440 #Frequency of Note A4
        keys = np.array([x+str(y) for y in range(0,9) for x in octave])
        # Trim to standard 88 keys
        start = np.where(keys == 'A0')[0][0]
        end = np.where(keys == 'C8')[0][0]
        keys = keys[start:end+1]

        note_freqs = dict(zip(keys, [2**((n+1-49)/12)*base_freq for n in range(len(keys))]))
        note_freqs[''] = 0.0 # stop

        return note_freqs
"""
note_freqs = get_piano_notes()
scale_intervals = ['A','a','B','C','c','D','d','E','F','f','G','g']

#Find index of desired key
index = scale_intervals.index('a')

#Redefine scale interval so that scale intervals begins with whichKey
new_scale = scale_intervals[index:12] + scale_intervals[:index]

"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    app.exec()
