#from eventlet.green import socket
#from eventlet.green import threading
#from eventlet.green import asyncore
#import eventlet
#eventlet.monkey_patch()
from api.auth import *
from api.wits import *
from flask import render_template


@app.route('/')
def index(): 
    return render_template('gen/index.html')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # socketio.run(app)
    app.run(host='127.0.0.1', port=8080, debug=True)

