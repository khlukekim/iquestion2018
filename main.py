
from flask import Flask, render_template, url_for
from pymongo import MongoClient
app = Flask(__name__)

@app.route('/')
def root():
  return render_template('main_plain.html', option={
    'sketchjs':url_for('static', filename='sketch.js'),
    'nanumfont':url_for('static', filename='NanumBarunGothicBold.otf'),
    'stylecss': url_for('static', filename='style.css'),
    'sampleimage': url_for('static', filename='images/')
    })

@app.route('/ex/<int:size>/<int:col>/<int:row>/<int:margin>')
def exhibit(size, col, row, margin):
  return render_template('exhibit_plain.html', option={
    'sketchjs':url_for('static', filename='sketch.js'),
    'nanumfont':url_for('static', filename='NanumBarunGothicBold.otf'),
    'stylecss': url_for('static', filename='style.css'),
    'sampleimage': url_for('static', filename='image/test1.png'),
    'size':size,
    'col': col,
    'row': row,
    'margin': margin,
    })


@app.route('/image', method='POST')
def upload_image():
  # todo
  # save image
  # process
  # insert
  #   time
  #   point
  #  filename
  #  n id
  #  hash id

@app.route('/perf/<int:width>/<int:height>')
def perform(width, height):
  return render_template('perform.html', option={
    'stylecss': url_for('static', filename='style.css'),
    'sampleimage': url_for('static', filename='images/'),
    'width': width,
    'height': height
    })

@app.route('/test')
def test():
  return render_template('image_upload_test.html')

class MongoDBConnection(object):
 # MongoDB Connection class for context manager
 # Check https://medium.com/@ramojol/python-context-managers-and-the-with-statement-8f53d4d9f87
 #
 # use like:
 # with MongoDBConnection(host, port) as mongo:
 #   collection = mongo.connection.dbname.collectionname
 #   data = collection.find()

  def __init__(self, host='localhost', port='27017'):
    self.host = host
    self.port = port
    self.connection = None

  def __enter__(self):
    self.connection = MongoClient(self.host, self.port)
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.connection.close()

