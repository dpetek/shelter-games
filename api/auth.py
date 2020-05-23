from flask import jsonify
from flask import request
from flask import session
from init import app, Session

@app.route('/api/login', methods = ['POST'])
def login():
    db_session = Session()
    name = request.get_json()["username"]

    if not verify_username(name):
        return jsonify({"error": "Wrong username format. Allowed special characters are numbers, '_' and '-'"})

    user = common.User(name=name, password=str(hash("")), admin = 0)
    db_session.add(user)
    db_session.commit()
    session["user"] = user.as_dict(db_session)

    return jsonify({"error": "", "user": user.as_dict(db_session)})

@app.route('/api/logout', methods = ['POST'])
def logout():
    if "user" in session:
        session.pop("user")
    return jsonify({"error": ""})

@app.route('/api/current_user', methods = ['GET'])
def current_user():
    if not "user" in session:
        return jsonify({"error": "User is not logged in..."})

    db_session = Session()
    current_user = db_session.query(common.User).filter_by(id = session["user"]["id"]).first()
    if not current_user:
        return jsonify({"error": "User is not logged in."})
    return jsonify({"error": "", "user": current_user.as_dict(db_session)})
