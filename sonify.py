from matplotlib import pyplot as plt
from PIL import Image
import numpy as np
from astropy.io import fits
import pandas as pd
import cv2
import sounddevice as sd
import time

# Reading Image

# img = Image.open("images/colors.jpg")
# imghsv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2HSV)
# plt.imshow(imghsv, cmap = 'viridis')
# plt.show()

img = Image(filename = "images/test/1.hdr")
img.format = 'bgr'
img.alpha_channel = False
img_arr = np.asarray(bytearray(img.make_blob()), dtype = 'float32')
# imghsv = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2HSV)
plt.imshow(imghsv, cmap = 'viridis')
plt.show()

exit(0)

hues = []
height, width, nlayers = imghsv.shape

# Traversing the image

for i in range(height):
    for j in range(width):
        hue = imghsv[i][j][0] # Take H value
        hues.append(hue)
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
npixels = 1000

amp = 0.5

for i in range(npixels):
    val = frequencies[i]
    note = amp * np.sin(2 * np.pi * val * t)
    song = np.concatenate([song, note])

sd.play(song)
time.sleep(len(t))
sd.stop()

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

