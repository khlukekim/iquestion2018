from __future__ import print_function

from PIL import Image
import numpy as np
import os
import cv2
import colorsys
import random
import argparse

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

from keras.models import load_model
from keras import backend as K
from keras.preprocessing.image import img_to_array, load_img
from skimage.io import imsave
from types import SimpleNamespace

initialized = False

kelvin_table = {
  2500: (255,161,72),
  9000: (214,225,255),
  12000: (195,209,255)}

def convert_temp(image,temp):
  r,g,b = kelvin_table[temp]
  matrix = ( r / 255.0, 0.0, 0.0, 0.0,
          0.0, g / 255.0, 0.0, 0.0,
          0.0, 0.0, b / 255.0, 0.0)
  return image.convert('RGB',matrix)


def normalize(x):
  return x / (K.sqrt(K.mean(K.square(x))) + 1e-11)

def sp_noise(image,prob):
  '''
  Add salt and pepper noise to image
  prob: Probability of the noise
  '''
  output = np.zeros(image.shape,np.uint8)
  thres = 1 - prob
  for i in range(image.shape[0]):
    for j in range(image.shape[1]):
      if rdn < prob:
        output[i][j] = 0
      elif rdn > thres:
        output[i][j] = 255
      else: 
        output[i][j] = image[i][j]
  return output

def deprocess_image(x):
  '''
  # normalize tensor: center on 0., ensure std is 0.1
  x -= x.mean()
  x /= (x.std() + K.epsilon())
  x *= 0.1

  # clip to [0, 1]
  x += 0.5
  x = np.clip(x, 0, 1)

  # convert to RGB array
  x *= 255
  '''

  x = np.clip(x, 0, 255).astype('uint8')
  return x

def rgb_to_hsv(rgb):
  rgb = rgb.astype('float')
  hsv = np.zeros_like(rgb)
  hsv[..., 3:] = rgb[..., 3:]
  r,g,b = rgb[...,0], rgb[...,1], rgb[...,2]
  maxc = np.max(rgb[...,:3],axis=-1)
  minc = np.min(rgb[...,:3],axis=-1)
  hsv[...,2] = maxc
  mask = maxc != minc
  hsv[mask,1] = (maxc-minc)[mask] / maxc[mask]
  rc = np.zeros_like(r)
  gc = np.zeros_like(g)
  bc = np.zeros_like(b)
  rc[mask] = (maxc-r)[mask] / (maxc-minc)[mask]
  gc[mask] = (maxc-g)[mask] / (maxc-minc)[mask]
  bc[mask] = (maxc-b)[mask] / (maxc-minc)[mask]
  hsv[...,0] = np.select(
    [r==maxc,g==maxc], [bc-gc,2.0+rc-bc],default=4.0+gc-rc)
  hsv[...,0] = (hsv[...,0] / 6.0) % 1.0
  return hsv


def hsv_to_rgb(hsv):
  rgb = np.empty_like(hsv)
  rgb[...,3:] = hsv[...,3:]
  h,s,v = hsv[...,0],hsv[...,1],hsv[...,2]
  i=(h*6.0).astype('uint8')
  f=(h*6.0)-i
  p=v*(1.0-s)
  q=v*(1.0-s*f)
  t=v*(1.0-s*(1.0-f))
  i=i%6
  conditions=[s==0.0,i==1,i==2,i==3,i==4,i==5]
  rgb[...,0] = np.select(conditions, [v,q,p,p,t,v],default=v)
  rgb[...,1] = np.select(conditions, [v,v,v,q,p,p],default=t)
  rgb[...,2] = np.select(conditions, [v,p,t,v,v,q],default=p)
  return rgb.astype('uint8')


def hueShift(arr, amount):
  hsv = rgb_to_hsv(arr)
  hsv[..., 0] = (hsv[..., 0]+amount) % 1.0
  rgb = hsv_to_rgb(hsv)
  return rgb  

#model = None
def init(args):
  return
  # load model
  global model, initialized
  model = load_model(args.weights)
  initialized = True

def train(args):
  
  height = args.height
  width = args.width
  weights = args.weights # 'weights.h5'
  source_file = args.filename # './jaemin.jpeg'
  dst_folder = args.savefolder # './generated'

  # set learning phase
  K.set_learning_phase(0)

  # load model
  model = load_model(weights)
  #model.summary()

  # load image
  im = load_img(source_file)
  im = im.resize((width,height))
  im = img_to_array(im)
  im = np.expand_dims(im,axis=0)
  print(im.shape)

  # set layer
  input_img = model.input
  layer_dict = dict([(layer.name, layer) for layer in model.layers[1:]])
  layer_name = 'dense_3'

  # set function
  layer_output = layer_dict[layer_name].output
  loss = K.mean(layer_output[:,1])
  grads = K.gradients(loss, input_img)[0]
  grads = normalize(grads)
  iterate = K.function([input_img], [loss,grads])

  # set layer for feature extraction
  layer_feature = 'activation_8'
  feature_output = layer_dict[layer_feature].output
  get_last_hidden_output = K.function([input_img],[feature_output])
  
  # get feature vector
  features = get_last_hidden_output([im])
  features = np.squeeze(features[0])

  # run
  prediction_list = []
  predt = model.predict(im)
  print(predt)
  prediction_list.append(predt[0][1])
  step = args.step #0.13 #100-1.0 # step size for gradient ascent
  for i in range(args.iter):
  
    # gradient ascent
    loss_value, grads_value = iterate([im])
    im += grads_value * step

    print('Current loss value:', loss_value)
    img = np.squeeze(im)
    img = deprocess_image(img)
    print(img.shape)
  

    # shift image
    if args.shift == 'on':
      rows, cols, depth = img.shape
      x_pos = np.random.normal(25,9)
      y_pos = np.random.normal(18,6)
      M = np.float32([[1,0,y_pos],[0,1,x_pos]])
      img_translated = cv2.warpAffine(img,M,(cols,rows))
      img_cropped = img_translated[50:950,36:688]

    # roll image
    if args.roll == 'on':
      A = img.shape[0] / 200 * i
      w = 2.0 / img.shape[1] * (i+1)
      func = lambda x: A * np.sin(2.0 * np.pi * x * w)
      for j in range(img.shape[1]):
        img[:,j,:] = np.roll(img[:,j,:], int(func(j)))

    # temperature
    if args.temp == 'on':
      ondo = args.ondo
      img = convert_temp(Image.fromarray(img),ondo)
      img = img_to_array(img)
      img = deprocess_image(img)


    save_name = '%s/%d.jpeg' % (dst_folder,i)

    if not os.path.exists(dst_folder):
      os.makedirs(dst_folder)

    imsave(save_name, img)

    img = np.expand_dims(img,axis=0)
    predt = model.predict(img)
    prediction_list.append(predt[0][1])

  K.clear_session()
  return prediction_list, features


def main(args):
  prediction_list, features = train(args)
  print(len(prediction_list), features.shape)

def run(inputFile, outputFolder):
  param = {
    'filename': inputFile,
    'savefolder': outputFolder,
    'temp': 'off',
    'roll': 'off',
    'shift': 'off',
    'iter': 10,
    'step': 1.2,
    'height': 400,
    'width': 400,
    'weights': '400weights_light.h5',
    'ondo': 9000
  }
  args = SimpleNamespace()
  for p in param:
    setattr(args, p, param[p])

  if (not initialized):
    init(args)

  return train(args)

if __name__ == '__main__':
  
  parser = argparse.ArgumentParser(description='viz filter')
  parser.add_argument('filename', type=str, metavar='FILE', help='FILENAME')
  parser.add_argument('savefolder', type=str, metavar='SAVEFOLDER', help='SAVE FOLDER')
  parser.add_argument('--temp', type=str, default='off', metavar='T', help='off,on')
  parser.add_argument('--roll', type=str, default='off', metavar='R', help='off,on')
  parser.add_argument('--shift', type=str, default='off', metavar='S', help='off,on')
  parser.add_argument('--iter', type=int, default=30, metavar='I', help='the number of iterations')
  parser.add_argument('--step', type=int, default=1.2, metavar='ST', help='steps')
  parser.add_argument('--height', type=int, default=400, metavar='H', help='height')
  parser.add_argument('--width', type=int, default=400, metavar='W', help='width')
  parser.add_argument('--weights', type=str, default='400weights_light.h5', metavar='WL', help='weights.h5')
  parser.add_argument('--ondo', type=int, default=9000, metavar='O', help='Temperature value')
  args = parser.parse_args()

  # run main
  main(args)


