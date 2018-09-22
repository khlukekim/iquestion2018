
from flask import Flask, render_template, url_for
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

@app.route('/perf/<int:width>/<int:height>')
def perform(width, height):
  return render_template('perform.html', option={
    'stylecss': url_for('static', filename='style.css'),
    'sampleimage': url_for('static', filename='images/'),
    'width': width,
    'height': height
    })