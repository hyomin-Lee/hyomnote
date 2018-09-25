from flask import *
import sqlite3
from contextlib import closing
from flask.cli import with_appcontext
import hashlib
#conn = sqlite3.connect("note.db")
#cs = conn.cursor()

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect("./note.db") 

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect("./note.db")
    return db

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register_form', methods = ['GET'])
def register_form():
    return render_template("register.html")

@app.route('/login_form', methods = ['GET'])
def login_form():
    return render_template("login.html")

@app.route('/register', methods = ['POST'])
def register():
    if request.form['pw'] != request.form['pw_c']:
        return '''<script>alert('not matched password!');location.href="/register_form";</script>'''
    else:
        cs = get_db()
        #check overlap
        query = '''select id from account where id= :Id'''
        check_id = cs.execute(query,{"Id":request.form['id']}).fetchall()
        if check_id == []:
            hash_pw = hashlib.sha256(request.form['pw']).hexdigest()
            query = '''INSERT INTO account VALUES (?, ?, ?, ?)'''
            cs.execute(query, (request.form['username'],request.form['id'],hash_pw, ""))
            cs.commit()
            return '''<script>alert('success register!');location.href="/";</script>'''
        else:
            return '''<script>alert('existed id');location.href="/register_form";</script>'''

@app.route('/login', methods = ['POST'])
def login():
    cs = get_db()
    check_id = cs.execute('''select id from account where id= :Id''',{"Id":request.form['id']}).fetchall()
    if check_id == []:
        return '''<script>alert('not exist id!');location.href="/";</script>'''
    else:
        query = '''select password from account where id=?'''
        db_pw = cs.execute(query,(request.form['id'],)).fetchall()[0][0]
        if db_pw == hashlib.sha256(request.form['pw']).hexdigest():
            return '''<script>alert('login success!!');location.href="/";</script>'''
        else :
            return '''<script>alert('wrong password!!');location.href="/";</script>'''

if __name__ in "__main__":
    app.run(host='0.0.0.0', port=8888)


