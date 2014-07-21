from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

from flask.ext.wtf import Form
from flask.ext.codemirror.fields import CodeMirrorField
from wtforms.fields import SubmitField

from flask.ext.codemirror import CodeMirror
import sys
from cStringIO import StringIO
import json

    

#Initialize Flask app from config file with codemirror extension
app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def cm():
    return render_template('index2.html')


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
