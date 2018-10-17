
from flask import Flask, render_template, url_for, request, jsonify, Response
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import datetime, os, time, random
from flask_socketio import SocketIO, join_room, leave_room
import gradient_ascent
from threading import Lock
from PIL import Image
from shutil import copyfile

app = Flask(__name__)
app.config['SECRET_KEY'] = 'naldskjfioqwjlksj'
socketio = SocketIO(app)
lock = Lock()

USER_IMAGE_FOLDER = os.path.join('static', 'images', 'userimage')
app.config['USER_IMAGE_FOLDER'] = USER_IMAGE_FOLDER

database_information = ['127.0.0.1', '27017'] 
app.config['pf-control-updated'] = []
app.config['pf-hash'] = 0
app.config['pf-images'] = []
app.config['using-model1'] = False

def get_option(d={}):
  o = {
    'sketchjs':url_for('static', filename='sketch.js'),
    'stylecss': url_for('static', filename='style.css'),
    'imageoriginal': url_for('static', filename='images/size_original/'),
    'image13': url_for('static', filename='images/size_13'),
    'image100': url_for('static', filename='images/'),
    'image56': url_for('static', filename='images/size_56/'),
    'jquery': url_for('static', filename='jquery-3.3.1.min.js'),
    'userimage': url_for('static', filename='images/userimage/'),
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
  with MongoDBConnection(database_information[0], database_information[1]) as mongo:
    coll = mongo.connection.iquestion.userImages
    last_images = list(coll.find(sort=[('created_at', -1)], limit=599))
    image_ids = [str(x['_id']) for x in last_images]
    image_scores = [x['score'] if 'score' in x else 0 for x in last_images]
    if len(image_ids) < 599:
      image_ids = ['%04d'%x for x in range(1000-(599-len(image_ids)+1), 1001)] + image_ids
      image_scores = [0 for x in range(1000 - (599-len(image_ids)+1), 1001)] + image_scores

  return render_template('main_plain.html', option=get_option({
    'image_ids': image_ids,
    'image_scores': image_scores
    }))

@app.route('/ex/<int:size>/<int:col>/<int:row>/<int:margin>')
def exhibit(size, col, row, margin):
  return render_template('exhibit_plain.html', option=get_option({
    'stylecss': url_for('static', filename='style.css'),
    'size':size,
    'col': col,
    'row': row,
    'margin': margin,
    }))

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

      filename = str(db_result.inserted_id)
      fileext = file.filename.split('.')[-1]
      filepath = os.path.join(app.config['USER_IMAGE_FOLDER'], filename + '.' + fileext)
      dirpath = os.path.join(app.config['USER_IMAGE_FOLDER'], filename)
      file.save(filepath)

      with lock:
        gradient_ascent.run(filepath, dirpath)

      #image = Image.open(os.path.join(dirpath, '9.jpg'))
      #imr = image.resize((13, 13))
      #image.save(os.path.join('static', 'images', 'size_original', filename + '.jpg'))
      copyfile(os.path.join(dirpath, '1.jpg'), os.path.join('static', 'images', 'size_original', filename+'.jpg'))     

      return jsonify({
        'r': 's',
        'i': filename
        })

@app.route('/pf-reset')
def pf_resuet():
  app.config['pf-images'] = [];

@app.route('/perf/<int:width>/<int:height>')
def perform(width, height):
  app.config['pf-control-updated'] = [];
  #app.config['pf-images'] = [];
  return render_template('perform.html', option=get_option({
    'width': width,
    'height': height,
    'fontsize': 64,
    'cellsize': 60
    }))

@app.route('/control')
def control():
  return render_template('control.html', option=get_option())

@app.route('/pf-update/<sessionHash>')
def pfUpdate(sessionHash):
  app.config['pf-hash'] = sessionHash
  counter = 0
  while len(app.config['pf-control-updated']) == 0 and counter < 10:
    counter += 1
    time.sleep(0.5)
  if len(app.config['pf-control-updated']) > 0:
    if (sessionHash == app.config['pf-hash']):
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
  else:
    return jsonify({
      'm': '',
      's': 'timeout'
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

@app.route('/check-print-status')
def check_print_status():
  return Response('na', mimetype='text/plain')

@app.route('/sockettest')
def sockettest():
  return render_template('sockettest.html')

@socketio.on('message')
def handle_message(message):
  print('received message: ' + str(message))
  socketio.send('server received: ' + str(message))

@socketio.on('perform join')
def handle_perform_join(sessionHash):
  room = 'perform'
  join_room(room)

@socketio.on('control message')
def handle_control_message(message):
  socketio.emit('control message', message, room='perform')

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
    socketio.run(app)
