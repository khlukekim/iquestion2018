
from flask import Flask, render_template, url_for, request, jsonify
from pymongo import MongoClient
from werkzeug.utils import secure_filename 
import datetime, os, time, random

app = Flask(__name__)

USER_IMAGE_FOLDER = os.path.join('static', 'userimage')
app.config['USER_IMAGE_FOLDER'] = USER_IMAGE_FOLDER

database_information = ['127.0.0.1', '27017']
with open('database') as f:
  database_information = [x.strip() for x in f.readlines()]

app.config['pf-control-updated'] = []
app.config['pf-hash'] = 0
app.config['pf-images'] = []

def get_option(d={}):
  o = {
    'sketchjs':url_for('static', filename='sketch.js'),
    'stylecss': url_for('static', filename='style.css'),
    'imageoriginal': url_for('static', filename='images/'),
    'image13': url_for('static', filename='images/'),
    'image100': url_for('static', filename='images/'),
    'jquery': url_for('static', filename='jquery-3.3.1.min.js')
    }
  if d:
    for k in d:
      o[k] = d[k]
  return o

@app.route('/')
def root():
  return render_template('park.html')

@app.route('/test')
def test():
  return render_template('main_plain.html', option=get_option())

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

@app.route('/image', methods=['POST'])
def upload_image():
  if 'user_image' not in request.files:
    # no file
    # what should I do?
    # maybe just redirect back
    # or use json error response
    return jsonify({
      'r': 'f',
      'c': 'nofile'
      })
  file = request.files['user_image']
  if file.filename == '':
    return jsonify({
      'r': 'f',
      'c': 'nofile'
      })
  if file:
    with MongoDBConnection(database_information[0], database_information[1]) as mongo:
      coll = mongo.connection.iquestion.userImages 
      data = {
        'created_at': datetime.datetime.now(),
        'prediction_point': 0,
        'original_filename': file.filename,
      } 
      db_result = coll.insert_one(data)

      filename = str(db_result.inserted_id) + '.' + file.filename.split('.')[-1]
      file.save(os.path.join(app.config['USER_IMAGE_FOLDER'], filename))
      
      return jsonify({
        'r': 's'
        })


@app.route('/perf/<int:width>/<int:height>')
def perform(width, height):
  app.config['pf-control-updated'] = [];
  app.config['pf-images'] = [];
  return render_template('perform.html', option=get_option({
    'width': width,
    'height': height,
    'fontsize': 64,
    'cellsize': 10
    }))

@app.route('/control')
def control():
  return render_template('control.html', option=get_option())

@app.route('/pf-update')
def pfUpdate():
  hash_value = random.getrandbits(100)
  app.config['pf-hash'] = hash_value
  while len(app.config['pf-control-updated']) == 0:
    time.sleep(0.5)
  if (hash_value == app.config['pf-hash']):
    message = app.config['pf-control-updated'][0]
    app.config['pf-control-updated'] = app.config['pf-control-updated'][1:]
    print('sending: ', message)
    return jsonify({
      'm': message
      })
  else :
    return jsonify({
      'm': '',
      's': 'hash changed'
      })

@app.route('/pf-message/<message>')
def pfMessage(message):
  app.config['pf-control-updated'].append(message)
  print('rec: ', app.config['pf-control-updated'])
  return jsonify({
    'r': 's'
    })

@app.route('/pf-upload-image')
def pf_upload_image_get():
  return render_template('pf_upload_image.html')
  
@app.route('/pf-upload', methods=['POST'])
def pf_upload_image():
  if 'user_image' not in request.files:
    # no file
    # what should I do?
    # maybe just redirect back
    # or use json error response
    return jsonify({
      'r': 'f',
      'c': 'nofile'
      })
  file = request.files['user_image']
  if file.filename == '':
    return jsonify({
      'r': 'f',
      'c': 'nofile'
      })
  if file:
    with MongoDBConnection(database_information[0], database_information[1]) as mongo:
      coll = mongo.connection.iquestion.userImages 
      data = {
        'created_at': datetime.datetime.now(),
        'prediction_point': 0,
        'original_filename': file.filename,
      } 
      db_result = coll.insert_one(data)

      filename = str(db_result.inserted_id) + '.' + file.filename.split('.')[-1]
      file.save(os.path.join(app.config['USER_IMAGE_FOLDER'], filename))
      app.config['pf-images'].append(filename)
      
      return jsonify({
        'r': 's'
        })

@app.route('/pf-update-image')
def pf_update_image():
  return jsonify({
      'r': 's',
      'f': app.config['pf-images']
      })

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
    self.port = int(port)
    self.connection = None

  def __enter__(self):
    self.connection = MongoClient(self.host, self.port)
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self.connection.close()

if __name__ == '__main__':
    app.run(threaded=True)