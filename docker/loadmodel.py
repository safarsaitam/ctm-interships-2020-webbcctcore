# Tensorflow 2.0 and Keras
# Import Tensorflow 2.0
import tensorflow as tf

# Import Keras from Tensorflow 2.0
import tensorflow.keras as keras

# Import Keras Modules form Tensorflow 2.0
from tensorflow.keras import backend as K

from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Conv2DTranspose, multiply, concatenate, Dense, Flatten, Dropout, Lambda
from tensorflow.keras.applications import VGG16
from tensorflow.keras.applications.vgg16 import preprocess_input
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import losses
from tensorflow.keras.applications.vgg16 import preprocess_input

def load_bcct_model():
  K.clear_session()
  model = load_model('15jan2019_14_30.hdf5')

  print('Model loaded with success')

  return model