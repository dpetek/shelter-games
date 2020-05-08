from flask import Blueprint, render_template

wits = Blueprint('profile', __name__, url_prefix='wits')

@wits.route('/')
def wits_index():
    s = select([Game])
    result = conn.execute(s)
    active_games = []
    for game in result:
        active_games.append(game)
    return render_template("wits/wits.html", title = "Wits & Wagers", games = active_games)

@wits.route('/wits/create', methods=['POST'])
def wits_create():
    rf = random.randint(1, 3)
    rq = random.randint(1, 24)
    qf = "%d_%d" % (rf, rq)
    stmt = sqlalchemy.text(
            "insert into game(name, state, question) values(:name, :state, :question)"
    )
    game_name = request.form["name"]
    try:
        conn.execute(stmt, name = game_name, state = 2, question = qf)
    except Exception as e:
        return {"error": str(e)}
    return {"error": "","game": {"name": game_name}}

@wits.route('/wits/delete', methods=['POST'])
def wits_delete():
    print (request.form)
    stmt = sqlalchemy.text(
            "delete from game where id = :id"
    )
    try:
        conn.execute(stmt, id = request.form["id"])
    except Exception as e:
        return {"error": str(e)}
    return {"error": ""}

@wits.route('/skip', methods=['POST'])
def wits_skip():
    rf = random.randint(1, 3)
    rq = random.randint(1, 24)
    qf = "%d_%d" % (rf, rq)
    stmt = sqlalchemy.text(
            "update game set question = :question where id = :id"
    )
    try:
        conn.execute(stmt, id = request.form["id"], question = qf)
    except Exception as e:
        return {"error": str(e)}
    return {"error": ""}

@wits.route('/enter', methods=['POST'])
def wits_enter():
    name = request.form["name"]
    # TODO Insert into db if it doesn't exist
    return jsonify({"user": session["name"]})

@app.route('/wits/answer', methods=['POST'])
def wits_answer():
    user = session["name"]
    answer = request.get_json()["answer"]
    return {"user": session["name"]}

@app.route('/wits/game/<id>')
def wits_game(id = None):
    s = select([Game])
    result = conn.execute(s)
    game = None
    for g in result:
        if str(g["id"]) == str(id):
            game = g

    if game == None:
        render_template("base/not_found.html")

    print(game)
    parts = game["question"].split("_")
    qf = "QA%s/q%s.jpg" % (parts[0], parts[1])
    af = "QA%s/a%s.jpg" % (parts[0], parts[1])

    return render_template("wits/wits_game.html",
            question_file = url_for('static', filename = qf),
            answer_file = url_for('static', filename = af),
            game = game)

