# -*- coding: utf-8 -*-
"""Untitled4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/160nlI9yFgYsTY_4xp8fH00oKR0xFwF_d
"""



import os
import numpy as np
import scipy.io
import cv2
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
from keras.utils import to_categorical
from sklearn.model_selection import train_test_split

img_labels = scipy.io.loadmat("imagelabels.mat")
img_labels = img_labels["labels"]
img_labels = img_labels[0]
for i in range(len(img_labels)):
  img_labels[i] = img_labels[i] - 1

train_x = []
train_y = []
dir = "jpg/"
i=1000
for imgs in os.listdir(dir):
  img_num = int(imgs[7:11])-1
  train_y.append(img_labels[img_num])
  image = cv2.imread(os.path.join(dir, imgs))
  resized = cv2.resize(image, (150,150))
  normalized_img = cv2.normalize(resized, None, alpha=0, beta=1, 
                            norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
  train_x.append(normalized_img)
  if(i):
    continue
  else:
    break
train_x = np.array(train_x)

trainx, valx, trainy, valy = train_test_split(train_x, train_y, test_size=0.5, random_state=10)

trainy = to_categorical(trainy)
valy = to_categorical(valy)

## INITIALIZING CONSTANTS
x = tf.placeholder(tf.float32, shape=[None, 150,150,3], name='x')
y = tf.placeholder(tf.float32, shape=[None, 102], name='y')
NUM_EPOCHS = 100
BATCH_SIZE = 500
KEEP_PROB = 0.5

graph = tf.Graph()
with graph.as_default():
    with tf.Session(graph=graph) as sess:
        tf.saved_model.loader.load(sess, ["serve"], 'model4')

        x = graph.get_tensor_by_name('x:0')
        y_preds = graph.get_tensor_by_name('y_preds:0')
        
        y_true = []
        preds = []
        for batch in range(int(len(valx)/BATCH_SIZE)):
          batch_x = valx[batch*BATCH_SIZE:min((batch+1)*BATCH_SIZE,len(valx))]
          batch_y = valy[batch*BATCH_SIZE:min((batch+1)*BATCH_SIZE,len(valy))]

          y_true.append(batch_y)
          preds.append(sess.run(y_preds, feed_dict={x: batch_x}))

        y_true = np.stack(np.array(y_true), axis=0)
        preds = np.stack(np.array(preds), axis=0)

# Calculte loss and accuracy
loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = tf.cast(preds, tf.float32), 
                                                              labels=tf.cast(y_true, tf.float32)))
correct = tf.equal(np.argmax(preds, axis=2), np.argmax(y_true, axis=2))
accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

# Printing results
with tf.Session() as sess:
    print('Loss :',loss.eval())
    print('Accuracy :', accuracy.eval())
