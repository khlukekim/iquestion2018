
from flask import Flask, render_template, url_for, request, jsonify, Response, session
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import datetime, os, time, random, threading, math
from flask_socketio import SocketIO, join_room, leave_room
import gradient_ascent
from threading import Lock
from PIL import Image
from shutil import copyfile
import test_model, word2word
import make_print_image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'naldskjfioqwjlksj'
app.secret_key = 'naldskjfioqwjlksj'
socketio = SocketIO(app)
lock = Lock()
app.config['tf-in-use'] = False

USER_IMAGE_FOLDER = os.path.join('static', 'images', 'userimage')
app.config['USER_IMAGE_FOLDER'] = USER_IMAGE_FOLDER

database_information = ['127.0.0.1', '27017']
app.config['pf-control-updated'] = []
app.config['pf-hash'] = 0
app.config['pf-images'] = []
app.config['pf-scores'] = []
app.config['print-image'] = 'na'

app.config['last-opened-ex-page'] = ''

def get_option(d={}):
  o = {
    'sketchjs':url_for('static', filename='sketch.js'),
    'stylecss': url_for('static', filename='_style.css'),
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

@app.route('/park')
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

@app.route('/')
def index_0():
  session['question_image'] = {}
  session['answer'] = {}
  return render_template('step00.html', option=get_option())

@app.route('/step01')
def index_1():
  if 'question_image' not in session:
    session['question_image'] = {}
  if 'image_1' not in session['question_image']:
    image = math.floor(random.random() * 1000) + 1
    session['question_image']['image_1'] = image
    with MongoDBConnection(database_information[0], database_information[1]) as mongo:
      row = mongo.connection.iquestion.authImages.find({'original_filename':'%04d.jpg'%image}).limit(1)[0]     
      session['question_image']['score_1'] = row['prediction_point']
  session.modified = True
  return render_template('step01.html', option=get_option({
    'question_image': '%04d'%session['question_image']['image_1'],
    'step': 1
    }))

t1 = ['오, 제 생각과 비슷하군요.', '나랑 감각이 통하는군요.', '네, 저도 같은 생각이에요.', '오, 저와 생각이 같군요.', '저도 같은 생각입니다.', '저처럼 보는 눈이 탁월하시군요', '저랑 잘 맞으실 거 같아요', '비슷한 감각을 가진 당신을 만나서 기뻐요', '우리는 비슷한 감각을 가졌나봐요', '보는 눈은 다 비슷하네요']
t2 = ['네, 저도 별로에요.', '나도 비슷한 생각이에요.', '저도 별로라고 생각했어요.', '생각하는게 저와 비슷하네요.', '사진 보는 눈이 저와 비슷하네요.', '휴, 당신도 저처럼 생각했군요', '별로에요, 그렇죠?', '당신이 봐도 별로군요!', '저만 별로라고 생각한 게 아니군요', '역시 저만 별로인게 아니었어요']
t3 = ['오, 당신의 감각이 좀 독특하군요', '저와 감각이 좀 다르군요', '제 생각과 다르군요', '저는 별로인데 생각이 다르군요', '저는 별로에요', '당신은 특별함을 찾아냈군요', '예술을 바라보는 눈이 개성있네요', '당신 덕에 예술을 새롭게 바라보게 돼요', '역시 보는 눈은 다 다른가봐요', '당신의 색다른 감각을 접수했어요']
t4 = ['저는 좋은데 생각이 다르군요.', '저와 보는 눈이 다르네요.', '보는 눈이 저랑 다르군요.', '저는 좋은데 보는 눈이 다르군요.', '보는 눈이 독특하네요.', '저는 무언가 특별해 보이더라구요', '역시 보는 눈은 모두 다르죠!', '저는 마음에 들어요 ', '당신 마음에는 안 드나보네요 ', '생각은 다 다를 수 있죠!']

def get_answer_message(p1, p2):
  r = math.floor(random.random()*10)
  p1 = int(p1)
  p2 = int(p2)
  if p1 > 0.5:
    if p2 > 0.5:  
      return t1[r]
    else:
      return t4[r]
  else:
    if p2 > 0.5:
      return t3[r]
    else:
      return t2[r]

@app.route('/step01a/<ans>')
def index_1a(ans):
  if 'answer' not in session:
    session['answer'] = {}
  session['answer']['ans_1'] = ans
  session.modified = True
  if 'question_image' in session and 'score_1' in session['question_image']:
    msg = get_answer_message(session['question_image']['score_1'], ans)
  else :
    msg = '이런, 문제가 생겼어요!'

  return render_template('step01a.html', option=get_option({
    'step': 1,
    'message': msg
    }))

@app.route('/step02')
def index_2():
  if 'question_image' not in session:
    session['question_image'] = {}
  if 'image_2' not in session['question_image']:
    image = math.floor(random.random() * 1000) + 1
    while image in list(session['question_image'].values()):
      image = math.floor(random.random() * 1000) + 1
    session['question_image']['image_2'] = image
    with MongoDBConnection(database_information[0], database_information[1]) as mongo:
      session['question_image']['score_2'] = mongo.connection.iquestion.authImages.find({'original_filename':'%04d.jpg'%image})[0]['prediction_point']

  session.modified = True
  return render_template('step01.html', option=get_option({
    'question_image': '%04d'%session['question_image']['image_2'],
    'step': 2
    }))

@app.route('/step02a/<ans>')
def index_2a(ans):
  if 'answer' not in session:
    session['answer'] = {}
  session['answer']['ans_2'] = ans

  session.modified = True
  return render_template('step01a.html', option=get_option({
    'step': 2,
    'message': get_answer_message(session['question_image']['score_2'], ans)
    }))

@app.route('/step03')
def index_3():
  if 'question_image' not in session:
    session['question_image'] = {}
  if 'image_3' not in session['question_image']:
    image = math.floor(random.random() * 1000) + 1
    while image in list(session['question_image'].values()):
      image = math.floor(random.random() * 1000) + 1
    session['question_image']['image_3'] = image
    with MongoDBConnection(database_information[0], database_information[1]) as mongo:
      session['question_image']['score_3'] = mongo.connection.iquestion.authImages.find({'original_filename':'%04d.jpg'%image})[0]['prediction_point']

  session.modified = True
  return render_template('step01.html', option=get_option({
    'question_image': '%04d'%session['question_image']['image_3'],
    'step': 3
    }))

@app.route('/step03a/<ans>')
def index_3a(ans):
  if 'answer' not in session:
    session['answer'] = {}
  session['answer']['ans_3'] = ans

  session.modified = True
  return render_template('step01a.html', option=get_option({
    'step': 3,
    'message': get_answer_message(session['question_image']['score_3'], ans)
    }))

@app.route('/step04')
def index_4():
  if 'question_image' not in session:
    session['question_image'] = {}
  if 'image_4' not in session['question_image']:
    image = math.floor(random.random() * 1000) + 1
    while image in list(session['question_image'].values()):
      image = math.floor(random.random() * 1000) + 1
    session['question_image']['image_4'] = image
    with MongoDBConnection(database_information[0], database_information[1]) as mongo:
      session['question_image']['score_4'] = mongo.connection.iquestion.authImages.find({'original_filename':'%04d.jpg'%image})[0]['prediction_point']

  session.modified = True
  return render_template('step01.html', option=get_option({
    'question_image': '%04d'%session['question_image']['image_4'],
    'step': 4
    }))

@app.route('/step04a/<ans>')
def index_4a(ans):
  if 'answer' not in session:
    session['answer'] = {}
  session['answer']['ans_4'] = ans

  session.modified = True
  if 'question_image' in session and 'answer' in session:
    with MongoDBConnection(database_information[0], database_information[1]) as mongo:
      coll = mongo.connection.iquestion.authAnswer
      data = {
          'created_at': datetime.datetime.now(),
          'image': session['question_image'],
          'answer': session['answer'],
        }
      db_result = coll.insert_one(data)

  return render_template('step01a.html', option=get_option({
    'step': 4,
    'message': get_answer_message(session['question_image']['score_4'], ans)
    }))

@app.route('/step05')
def index_5():
  return render_template('step05.html', option=get_option())

@app.route('/step06')
def index_6():
  return render_template('step06.html', option=get_option())

@app.route('/step08')
def index_8():
  with MongoDBConnection(database_information[0], database_information[1]) as mongo:
    coll = mongo.connection.iquestion.userImages
    last_images = list(coll.find().hint([('$natural',-1)]).limit(599))
    image_ids = [str(x['_id']) for x in last_images]
    image_scores = [x['prediction_point'] if 'prediction_point' in x else 0 for x in last_images]
    if len(image_ids) < 599:
      n = 599-len(image_ids)
      image_ids = ['%04d'%x for x in range(1000 - n, 1001)] + image_ids
      auth_scores = list(mongo.connection.iquestion.authImages.find().hint([('$natural',-1)]).limit(n))
      auth_scores = [x['prediction_point'] for x in auth_scores]
      auth_scores.reverse()
      image_scores = auth_scores + image_scores
    
    scores = image_scores + [session['user_score']]
    positions = list(range(len(scores)))
    sorted_positions = sorted(positions, key=lambda x:scores[x], reverse=True)
    image_ids = image_ids + [session['user_image']]
    image_ids = [image_ids[x] for x in sorted_positions]

  return render_template('step08.html', option=get_option({
      'image_ids': image_ids,
      'user_image': session['user_image'],
      'rank': sorted_positions.index(len(positions)-1)+1
    }))

@app.route('/step09')
def index_9():
  with MongoDBConnection(database_information[0], database_information[1]) as mongo:
    coll = mongo.connection.iquestion.userImages
    last_images = list(coll.find({},{'prediction_point':1}))
    image_scores = [x['prediction_point'] if 'prediction_point' in x else 0 for x in last_images]
    scores = image_scores + [session['user_score']]
    positions = list(range(len(scores)))
    sorted_positions = sorted(positions, key=lambda x:scores[x], reverse=True)

  return render_template('step09.html', option=get_option({
      'n_images': len(positions),
      'rank': sorted_positions.index(len(positions)-1)+1
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

      while app.config['tf-in-use']:
        time.sleep(1)
      with lock:
        try:
          app.config['tf-in-use'] = True
          result = gradient_ascent.run(filepath, dirpath)
          app.config['tf-in-use'] = False
        except Exception as e:
          app.config['tf-in-use'] = False
          return jsonify({
            'r': 'f',
            })

      coll.update({'_id':db_result.inserted_id},{'prediction_point':int(result[0][0]*100)})
      #image = Image.open(os.path.join(dirpath, '9.jpg'))
      #imr = image.resize((13, 13))
      #image.save(os.path.join('static', 'images', 'size_original', filename + '.jpg'))
      copyfile(os.path.join(dirpath, '1.jpg'), os.path.join('static', 'images', 'size_original', filename+'.jpg'))

      session['user_image'] = filename
      session['user_score'] = int(result[0][0]*100)
      return jsonify({
        'r': 's',
        'i': filename
        })
      



@app.route('/pf-reset')
def pf_reset():
  app.config['pf-images'] = [];
  app.config['pf-scores'] = [];
  return jsonify({
    'r': 's'
    })

@app.route('/perf/<int:width>/<int:height>')
def perform(width, height):
  app.config['pf-control-updated'] = [];
  #app.config['pf-images'] = [];
  return render_template('perform.html', option=get_option({
    'width': width,
    'height': height,
    'fontsize': 64,
    'cellsize': 56
    }))

@app.route('/control')
def control():
  return render_template('control.html', option=get_option())

@app.route('/pf-get-tags/<file>')
def pfGetTags(file):
  with lock:
    try:
      app.config['tf-in-use'] = True
      tags, caption = test_model.run(os.path.join(USER_IMAGE_FOLDER,file))
      app.config['tf-in-use'] = False
    except Eception:
      app.config['tf-in-use'] = False
      return jsonify({'r':'f', 't':'실패', 'c': ''})
  return jsonify({'r':'s','t':tags, 'c':caption})

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
      t = threading.Thread(target=process_image, args=(str(db_result.inserted_id),file.filename.split('.')[-1]))
      t.start()

      return jsonify({
        'r': 's'
        })


def process_image(filename, fileext):
  filepath = os.path.join(app.config['USER_IMAGE_FOLDER'], filename + '.' + fileext)
  dirpath = os.path.join(app.config['USER_IMAGE_FOLDER'], filename)

  while app.config['tf-in-use']:
    time.sleep(1)
  with lock:
    try:
      app.config['tf-in-use'] = True
      score, feature = gradient_ascent.run(filepath, dirpath)
      app.config['tf-in-use'] = False
    except Eception:
      app.config['tf-in-use'] = False
      print('processing_failed')
      return False

  #image = Image.open(os.path.join(dirpath, '9.jpg'))
  #imr = image.resize((13, 13))
  #image.save(os.path.join('static', 'images', 'size_original', filename + '.jpg'))
  target = os.path.join('static', 'images', 'size_original', filename+'.jpg')
  copyfile(os.path.join(dirpath, '1.jpg'), target)
  app.config['pf-images'].append(filename + '.jpg')
  print(score[0])
  app.config['pf-scores'].append(int(10000 * score[0]))
  print('processing_done: '+filename)
  return True

@app.route('/pf-w2w/<word>')
def pf_w2w(word):

  while app.config['tf-in-use']:
    time.sleep(1)
  with lock:
    try:
      app.config['tf-in-use'] = True
      words = word2word.main(word)
      app.config['tf-in-use'] = False
    except Eception:
      app.config['tf-in-use'] = False
      return jsonify({'r':'f', 'w':'실패'})
  print(word, words)
  return jsonify({
    'r': 's',
    'w': words
    })

@app.route('/pf-update-image')
def pf_update_image():
  return jsonify({
      'r': 's',
      'f': app.config['pf-images'],
      's': app.config['pf-scores']
      })

@app.route('/check-print-status')
def check_print_status():
  return Response(app.config['print-image'], mimetype='text/plain')

@app.route('/make-printable-image')
def make_printable_image():
  app.config['print-image'] = make_print_image.main()
  return jsonify({'r':'s'})

@app.route('/sockettest')
def sockettest():
  return render_template('sockettest.html')

@socketio.on('message')
def handle_message(message):
  print('received message: ' + str(message))
  socketio.send('server received: ' + str(message))

@socketio.on('perform join')
def handle_perform_join(sessionHash):
  print(sessionHash)
  room = 'perform'
  join_room(room)

@socketio.on('control message')
def handle_control_message(message):
  print(message)
  socketio.emit('control message', message, room='perform')

@socketio.on('connect')
def onsockcon():
  print('socket connected')

@socketio.on_error()
def socketerror(e):
  print(e)

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
    socketio.run(app, host='0.0.0.0', port=80)
