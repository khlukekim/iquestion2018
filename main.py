from flask import Flask, render_template, url_for
app = Flask(__name__)

@app.route('/')
def root():
    return render_template('main_plain.html', option={
      'sketchjs':url_for('static', filename='sketch.js'),
      'nanumfont':url_for('static', filename='NanumBarunGothicBold.otf'),
      'stylecss': url_for('static', filename='style.css'),
      'sampleimage': url_for('static', filename='image/image')
      })