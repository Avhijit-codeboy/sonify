import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt6 import QtWidgets
from PyQt6.QtCore import QCoreApplication, QDir, Qt, QFileInfo
from PyQt6.QtGui import QAction, QIcon, QKeySequence
from PyQt6.QtWidgets import (QComboBox, QFileDialog, QLabel, QPushButton, QStatusBar, QWidget, QApplication, QMainWindow,
                             QSplitter, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QMenu, QMenuBar, QSizePolicy
                             )
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
import threading
import resources

# Global Variables
IMAGE_DIR = "images/"

# Main Window class
class MainWindow(QMainWindow):
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
        self.drawerLayout.addWidget(self.playButton, 2, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)

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

            self.Msg("Loading Image", 2)
            self.ReadImage()
            self.Msg("Image Loaded", 5)

        self.playButton.setEnabled(True)

    def FileSize(self):
        return str(QFileInfo(self.file).size())

    def Hue2freq(self, h,scale_freqs):
        thresholds = [26 , 52 , 78 , 104,  128 , 154 , 180]
        note = scale_freqs['C4']
        if (h <= thresholds[0]):
            note = scale_freqs['B3']
        elif (h > thresholds[0]) & (h <= thresholds[1]):
            note = scale_freqs['a3']
        elif (h > thresholds[1]) & (h <= thresholds[2]):
            note = scale_freqs['G3']
        elif (h > thresholds[2]) & (h <= thresholds[3]):
            note = scale_freqs['f3']
        elif (h > thresholds[3]) & (h <= thresholds[4]):    
            note = scale_freqs['E2']
        elif (h > thresholds[4]) & (h <= thresholds[5]):
            note = scale_freqs['d2']
        elif (h > thresholds[5]) & (h <= thresholds[6]):
            note = scale_freqs['F3']
        else:
            note = scale_freqs['C1']
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
        self.aboutMenu = QMenu("&About")

        self.menubar.addMenu(self.fileMenu)
        self.menubar.addMenu(self.editMenu)
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

    # Function that handles the play button click
    def Play(self):
        self.PlayAudio()
        #self.MoveHorizLine()

    # Function to play audio
    def PlayAudio(self):
        sd.play(self.song)
        time.sleep(5)
        sd.stop()

    def MoveHorizLine(self):
        pass

    # Function for reading the image
    def ReadImage(self):
        self.img = Image.open(self.file)
        self.imghsv = cv2.cvtColor(np.array(self.img), cv2.COLOR_BGR2HSV)
        self.ax.imshow(self.img)
        self.UpdateCanvas()

        # Update the statusbar info
        self.status_fileName.setText(self.file)
        self.status_fileSize.setText(self.FileSize())
        self.status_fileDim.setText(str(self.imghsv.shape))

        self.Sonify()

    # Function that handles the sonification
    def Sonify(self):
        self.hues = []
        self.img_height, self.img_width, self.img_nlayers = self.imghsv.shape

        self.MapHorizontal_LR(4, 10)

        self.hues = pd.DataFrame(self.hues, columns= ["hues"])

        #Get oiani frequencies
        scale_freqs2 = self.get_Piano_Notes()
        #Map thses frequencies to hue values
        self.hues['notes'] = self.hues.apply(lambda row : self.Hue2freq(row['hues'],scale_freqs2), axis = 1)

        frequencies = self.hues['notes'].to_numpy() #convert to numpy array

        self.song = [] #array to store piano waveforms

        self.SAMPLE_RATE = 44100

        T = 0.2 #duration of each waveform

        self.t = np.linspace(0, T, int(T * self.SAMPLE_RATE), endpoint = False)

        # npixels = 100

        amp = 100

        for i in range(len(frequencies)):
            val = frequencies[i]
            fundamental_note = np.sin(2 * np.pi * val * self.t)
            #create harmonics as well as apply ADSR envelope
            harmonic_frequencies = [amp*fundamental_note, 2 * fundamental_note*(amp/2), 3 * fundamental_note*(amp/3), 4 * fundamental_note*(amp/4), 5 * fundamental_note*(amp/5)]
            piano_waveform = np.zeros_like(fundamental_note)
            # Add harmonics to the sine wave
            for harmonics in harmonic_frequencies:
                piano_waveform+=harmonics
            # Normalize the waveform
            piano_waveform /= np.max(np.abs(piano_waveform))
            # Append the waveforms
            self.song = np.concatenate([self.song, piano_waveform])
        
        
    """""
    Piano code
    """""
    def get_Piano_Notes(self):   
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
    
    # Helper function for showing message in the statusbar
    def Msg(self, msg = None, t = 1):
        self.statusbar.showMessage(msg, t * 1000)

    # Helper function to update canvas
    def UpdateCanvas(self):
        self.canvas.draw()

    def MapHorizontal_LR(self, skipw, skiph):
        for j in range(0, self.img_width, int(skipw % self.img_width)):
            for i in range(0, self.img_height, int(skiph % self.img_height)):
                hue = self.imghsv[i][j][0]
                self.hues.append(hue)
                # np.concatenate([self.hues, hue])
"""
---------------------------------------------------------------------------------------------------------------------------------------------------------------
"""
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    app.exec()
