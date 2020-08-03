# -*- coding: utf-8 -*-
"""deepfunguy.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1PBzrfsscrEIuDbxDkqS3RGiw_rjuTdM4
"""

# import zipfile
# with zipfile.ZipFile('promoter_all.zip', 'r') as zip_ref:
#     zip_ref.extractall()

!unzip promoter_all.zip

cd ../

cd combined/

!ls -1 | wc -l

import sys
import numpy as np
import pandas as pd
import os
from tqdm import tqdm
from natsort import natsorted

import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler,MinMaxScaler,LabelBinarizer

import keras
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Dropout, Activation, Concatenate, Flatten, MaxPooling2D, Convolution2D, Convolution1D, MaxPooling1D, GlobalMaxPooling1D, BatchNormalization, LSTM, GRU, Bidirectional
from keras.regularizers import l2,l1
from keras.optimizers import SGD,Adam,RMSprop
from tensorflow.compat.v1 import InteractiveSession
import keras.backend as K
from keras.preprocessing.image import array_to_img, img_to_array, load_img
from keras.callbacks import EarlyStopping, ModelCheckpoint,ReduceLROnPlateau
from keras.models import load_model

from keras.metrics import AUC, Precision, Recall

label = pd.read_csv('label.csv')['label'].values

#label = np.asarray(label).reshape(-1,1)

### use label encoder
lb = LabelBinarizer()
label = lb.fit_transform(label)

label
# done label

data = natsorted(os.listdir('combined/'))

len(data)
data[:4]

#len(off),len(target)
samples = len(data)

# height x width is the standard
dims = (4,300)
#ideal 4x28
# 54x390
shape = (samples, dims[0], dims[1], 1)     

dataset = np.ndarray(shape=shape,dtype=np.float32)

i=0
for item in data:
    img1 = load_img('combined/'+ item, target_size=dims, color_mode='grayscale',interpolation='nearest')  # this is a PIL image
    # Convert to Numpy Array
    x1 = img_to_array(img1)
    dataset[i] = x1
    i += 1
    if i % 1000 == 0:
        print("%d images to array" % i)

print("All images done!")

dataset.shape, label.shape

# train test split for 1D convolution
dataset1d = dataset.squeeze()
dataset_train, dataset_test, label_train, label_test = train_test_split(dataset1d, label, test_size=0.2, random_state=1)

dataset_train.shape, label_train.shape, dataset_test.shape, label_test.shape

try:
  del model, history
except:
  pass

from keras import backend as K
K.clear_session()

# # 1D conv:
input_1 = Input(shape = (4,300))

conv1_1 = Convolution1D(32, 3, activation = 'relu',padding='same',kernel_regularizer=l2(5.0))(input_1)
pool1_1 = MaxPooling1D(pool_size=2)(conv1_1)

conv1_2 = Convolution1D(64, 3, activation = 'relu',padding='same',kernel_regularizer=l2(5.0))(pool1_1)
pool1_2 = MaxPooling1D(pool_size=2)(conv1_2)

#bilstm1_1 = Bidirectional(GRU(1024, return_sequences=True))(pool1_2)
flat_1 = Flatten()(pool1_2)
 
dense1   = Dense(64, activation = 'relu')(flat_1 )
dropout =  Dropout(0.5)(dense1)
dense2   = Dense(64, activation = 'relu')(dropout)
#dense3   = Dense(1024, activation = 'relu')(dense2)
output   = Dense(1, activation = 'sigmoid')(dense2)
 
# # create model with two inputs
model = Model(inputs=[input_1], outputs=[output])

model.summary()

model.compile(loss='binary_crossentropy',optimizer='rmsprop',metrics=['accuracy'])

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.1,patience=5, min_lr=0.00001, verbose=1)

model_checkpoint = ModelCheckpoint('checkpoint.hdf5', monitor='val_loss', verbose=1, save_best_only=True, mode='min')

history=model.fit(dataset_train, label_train, 
                batch_size=128,epochs=50,verbose=1, 
                validation_data=(dataset_test,label_test),
                callbacks=[model_checkpoint,reduce_lr])

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

fig = plt.figure(figsize=(15,5))
plt.subplot(1,2,1)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title("Classification Losses")
plt.ylabel("Losses")
plt.xlabel("Epoch")
plt.legend(["Training Loss","Validation Loss"])
plt.subplot(1,2,2)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title("Accuracy")
plt.ylabel("Accuracy")
plt.xlabel("Epoch")
plt.legend(["Training Accuracy","Validation Accuracy"])
plt.show()

#load best model
from keras.models import load_model
bm = load_model('checkpoint.hdf5')

#model predictions
ypred = bm.predict(dataset_test,batch_size=128)

labelpred = np.where(ypred > 0.5, 1, 0)
#print(labelpred)

from sklearn import metrics

print(metrics.confusion_matrix(label_test, labelpred))

print(metrics.classification_report(label_test, labelpred, digits=3))

#gradcam tutorial

#get image index
indexes = np.array(range(10202)).reshape(-1,1)
indexes_train, indexes_test = train_test_split(indexes, test_size=0.2, random_state=1)

indexes_train.shape, indexes_test.shape

#get the maximum probability
vals = ypred.tolist()
vals[:20]

indexes_test[:20]

index_img = 5174
cam_img = dataset1d[index_img].reshape(1,4,300)

cam_img.shape

plt.imshow(dataset1d[index_img], cmap='gray')

prediction = bm.predict(cam_img)

prediction

#target class is 1

last_conv = model.get_layer('conv1d_2')

model.output

grads = K.gradients(model.output[:,0],last_conv.output)[0]

grads

pooled_grads = K.mean(grads,axis=(0,1,2))
iterate = K.function([model.input],[pooled_grads,last_conv.output[0]])
pooled_grads_value,conv_layer_output = iterate([cam_img])

pooled_grads_value,conv_layer_output.shape

for i in range(64):
    conv_layer_output[:,i] *= pooled_grads_value
#heatmap = np.mean(conv_layer_output,axis=-1)

conv_layer_output.shape

heatmap = np.mean(conv_layer_output,axis=0)

heatmap = heatmap.reshape(1,64)

plt.imshow(heatmap)

plt.imshow(heatmap)

for x in range(heatmap.shape[0]):
    for y in range(heatmap.shape[1]):
        heatmap[x,y] = np.max(heatmap[x,y],0)

plt.imshow(heatmap)

heatmap

heatmap = np.maximum(heatmap,0)
#heatmap /= np.max(heatmap)

heatmap

plt.imshow(heatmap)

#import cv2

from skimage.transform import resize

#plt.figure(figsize=(4,300))
upsample = resize(heatmap, (4,300),preserve_range=True)
#plt.imshow(cam_img.squeeze(), cmap='gray')
#plt.imshow(upsample,alpha=1)

#plt.show()

fig, ax = plt.subplots(figsize=(300, 4))
ax.imshow(cam_img.squeeze(), cmap='BuPu',interpolation='nearest')
#ax.imshow(upsample, interpolation='nearest',alpha=0.5,cmap='viridis')
plt.axis('off')

