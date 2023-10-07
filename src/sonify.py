from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename
import pandas as pd
import scipy as sp
import cv2
import sounddevice as sd
import time

# Reading Image

# JPG / PNG / TIF
#FILE = "../images/New/orion_vis_ir_xfade_dome_030_v5-3840x3840p60.{}.png"
#img = Image.open(FILE.format(1210))
img = Image.open("../images/colors.jpg")
imghsv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2HSV)
plt.imshow(imghsv)
plt.show()

# FITS
# img_data = fits.getdata("../images/skv.fits")
# plt.imshow(img_data)
# plt.show()

hues = []
height, width, nlayers = imghsv.shape

# Traversing the image

def map_stack(skipw = width, skiph = height):
    for i in range(0, height, int(height / skiph)):
        for j in range(0, width, int(width / skipw)):
            hue = imghsv[i][j][0] # Take H value
            hues.append(hue)

def map_horizontal(skipw = width, skiph = height):
    for j in range(0, width, int(skipw % width)):
        for i in range(0, height, int(skiph % height)):
            hue = imghsv[i][j][0]
            hues.append(hue)

def map_vertical(skipw = width, skiph = height):
    for j in range(1, width, int(width / skipw)):
        for i in range(0, height, int(height /  skiph)):
            hue = imghsv[i][j][0]
            hues.append(hue)

map_horizontal(5, 10)
hues = pd.DataFrame(hues, columns= ["hues"])

#Define frequencies that make up A-Harmonic Minor Scale
scale_freqs = [220.00, 246.94 ,261.63, 293.66, 329.63, 349.23, 415.30] 

def hue2freq(h,scale_freqs):
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

hues['notes'] = hues.apply(lambda row : hue2freq(row['hues'],scale_freqs), axis = 1)
frequencies = hues['notes'].to_numpy()
song = np.array([])
sr = 22050
T = 0.1
t = np.linspace(0, T, int(T * sr), endpoint = False)
npixels = 100

amp = 0.5

print(len(frequencies))
for i in range(len(frequencies)):
    val = frequencies[i]
    note = amp * np.sin(2 * np.pi * val * t)
    song = np.concatenate([song, note])

sd.play(song)
time.sleep(5)
sd.stop()
exit(0)

def get_piano_notes():   
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

note_freqs = get_piano_notes()
scale_intervals = ['A','a','B','C','c','D','d','E','F','f','G','g']

#Find index of desired key
index = scale_intervals.index('a')

#Redefine scale interval so that scale intervals begins with whichKey
new_scale = scale_intervals[index:12] + scale_intervals[:index]
