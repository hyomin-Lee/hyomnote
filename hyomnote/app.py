from flask import *
import sqlite3
from contextlib import closing
from flask.cli import with_appcontext
import hashlib
from flask_wtf import Form
from flask_pagedown.fields import PageDownField
from wtforms.fields import SubmitField
from flask_pagedown import PageDown
#conn = sqlite3.connect("note.db")
#cs = conn.cursor()


app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = 'secret_code_hyomin_baobob'
pagedown = PageDown(app)

class PageDownFormExample(Form):
    pagedown = PageDownField('asdfasdfasdfasdfasdfadf')
    submit = SubmitField('Save')

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
    if session.get('LogFlag') == True:
        return render_template('session_index.html', name=session.get('UserId'))
    else:
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
            session['LogFlag'] = True
            query = '''select username from account where id=?'''
            session['UserId'] = cs.execute(query, (request.form['id'],)).fetchall()[0][0]
            return '''<script>alert('login success!!');location.href="/";</script>'''
        else :
            return '''<script>alert('wrong password!!');location.href="/";</script>'''

@app.route('/logout', methods = ['get'])
def logout():
    session['LogFlag'] = False
    session.pop('UserId', None)
    return redirect(url_for('index'))

@app.route('/usernote', methods = ['get'])
def usernote():
    if session.get('LogFlag') != True:
        return  '''<script>alert('not allowed! plz retry..');location.href="/";</script>'''
    else:
        form = PageDownFormExample()
        cs = get_db()
        form.pagedown.data = cs.execute('''select board from account where username=?''',(session.get('UserId'),)).fetchall()[0][0]
        return render_template('note.html', form=form)

@app.route('/note_submit', methods = ['post'])
def note_submit():
    cs = get_db()
    query = '''update account set board=? where username=?'''
    cs.execute(query,(request.form['pagedown'], session.get('UserId')))
    cs.commit()
    return redirect(url_for('usernote'))

if __name__ in "__main__":
    app.run(host='0.0.0.0', port=80)


