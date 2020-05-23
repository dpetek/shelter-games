from eventlet.green import socket
from eventlet.green import threading
from eventlet.green import asyncore
import eventlet
eventlet.monkey_patch()

from api.auth import *
from api.wits import *
from constants import *
from flask import render_template
from init import *
import re

def verify_username(username):
    return True
    # return re.match("^[A-Za-z0-9_-]{3,15}$", username)

@socketio.on('message')
def wits_socket_connected(message):
    # Process messages received from the client.
    pass

@app.route('/')
def index(): 
    return render_template('gen/index.html')

@app.route('/codenames/game/<id>')
def codenames_game(id):
    return render_template("codenames/codenames.html")


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    socketio.run(app)

