# Keypoint Predicting Function
# import webbcct.settings as sett
# Imports
import numpy as np

# import matplotlib.pyplot as plt
# from matplotlib.figure import Figure

#from matplotlib.backends.backend_agg import FigureCanvasAgg
#from matplotlib.backends.backend_svg import FigureCanvas
#import matplotlib as mpl
#import matplotlib.path as mpath
#import matplotlib.patches as mpatches
from django.http import HttpResponse
from django.shortcuts import render
import cv2
import io
import platform


# Tensorflow 2.0 and Keras
# Import Tensorflow 2.0
import tensorflow as tf

# Import Keras from Tensorflow 2.0
import tensorflow.keras as keras

# Import Keras Modules form Tensorflow 2.0
from tensorflow.keras import backend as K

from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Conv2DTranspose, multiply, concatenate, Dense, Flatten, \
    Dropout, Lambda
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import losses
from tensorflow.keras.applications.vgg16 import preprocess_input


# def load_bcct_model():
#     K.clear_session()
#     #model.load_weights('../code/utils/15jan2019_14_30.hdf5')
#     print('Model loaded with success')
#
#     return model

# K.clear_session()
# Load Model
# Docker Deployment
# model = load_model('../code/utils/15jan2019_14_30.hdf5')
# model.load_weights('../code/utils/15jan2019_14_30.hdf5')

# Personal Computer Deployment
model = load_model('utils/15jan2019_14_30.hdf5')
model.load_weights('utils/15jan2019_14_30.hdf5')

def keypoint_prediction(image):
    image = preprocess_input(image)
    #Load Keras Model
    #model = load_bcct_model()

    predicted_keypoints = model.predict(image.reshape((1, image.shape[0], image.shape[1], image.shape[2])))[3]
    predicted_keypoints = predicted_keypoints.reshape((74,))
    predicted_keypoints *= 512
    #Clear Session To Prevent Tensor Errors
    K.clear_session()

    return predicted_keypoints

#Image & Keypoints Plot Function
# def plot_img_keypoints(keypoints):
#     x = keypoints[0:68:2]
#     y = keypoints[1:69:2]
#
#     #fig=Figure()
#     #ax=fig.add_subplot(111)
#     plt.axis([0, 512, 384, 0])
#     plt.plot(x, y,matplotlib 'o')
#
#     #ax.set(xlabel='time (s)', ylabel='voltage (mV)',
#     #       title='About as simple as it gets, folks')
#     #ax.grid()
#
#     buf = io.BytesIO()
#     plt.savefig(buf, format='svg', bbox_inches='tight')
#     s = buf.getvalue()
#     buf.close()
#
#     plt.cla() # clean up plt so it can be re-used
#     response = HttpResponse(s, content_type='image/svg+xml')
#     return response
#

def bra_size_converter(bra_cup):
  thorax_size_map = [i for i in range(60, 101, 5)]
  cup_size_map = ['AA', 'A', 'B', 'C', 'D', 'DD', 'E', 'F', 'FF', 'G', 'GG', 'H', 'HH', 'J', 'JJ', 'K']

  breast_size_grid = np.array([
    [i for i in np.linspace(69, 106.5, len(cup_size_map))],
    [i for i in np.linspace(74, 111.5, len(cup_size_map))],
    [i for i in np.linspace(79, 116.5, len(cup_size_map))],
    [i for i in np.linspace(84, 121.5, len(cup_size_map))],
    [i for i in np.linspace(89, 126.5, len(cup_size_map))],
    [i for i in np.linspace(94, 131.5, len(cup_size_map))],
    [i for i in np.linspace(99, 136.5, len(cup_size_map))],
    [i for i in np.linspace(104, 141.5, len(cup_size_map))],
    [i for i in np.linspace(109, 146.5, len(cup_size_map))]
  ])

  thorax_size = int(''.join([x for x in bra_cup if x.isdigit()]))
  # print(thorax_size)
  cup_size = ''.join([x for x in bra_cup if x.isalpha()])
  # print(cup_size)

  thorax_coord = thorax_size_map.index(thorax_size)
  # print(thorax_coord)
  cup_coord = cup_size_map.index(cup_size)
  # print(cup_coord)

  breast_size = breast_size_grid[thorax_coord, cup_coord]

  return breast_size



def compute_euclidean_distance(a, b):
  return np.sqrt(np.sum((a-b)**2))
