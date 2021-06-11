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
    app.run(host='127.0.0.1', port=8080, debug=True)

