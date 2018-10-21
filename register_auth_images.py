from pymongo import MongoClient
conn = MongoClient('localhost', 27017)
coll = conn.iquestion.authImages

import numpy
y = numpy.load('Y.npy').mean(1)
y = y > 2.5
import datetime
for i in range(1000):
  data = {
    'created_at': datetime.datetime.now(),
    'prediction_point': int(y[i]),
    'original_filename': '%04d.jpg'%(i+1)
  }
  coll.insert_one(data)