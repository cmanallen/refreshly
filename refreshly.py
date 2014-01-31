# IMPORT
import os
import sqlite3
import functools
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, _app_ctx_stack
from contextlib import closing
from werkzeug import secure_filename


# CONFIG
DATABASE = '/tmp/refreshly.db'
DEBUG = True
SECRET_KEY = 'dev_key' #dont do something simple


# FILE UPLOAD
UPLOAD_FOLER = '/static/uploads'
ALLOWED_EXTENSIONS = set(['tar.gz', 'tgz', 'tar.bz2', 'tbz', 'zip'])


# APP STARTUP
app = Flask(__name__)
app.config.from_object(__name__)


# NAVIGATION
sort = {
    "Gnome": ["Shell", "GTK", "GDM"],
    "KDE": ["Plasma", "QT-Themes", "KDM"],
    "XFCE": ["Themes"],
    "Pantheon": ["Shell", "eGTK", "LDM", "Icons"],
    "Cinnamon": ["Shell", "GTK", "MDM"],
}

sgsgs = sorted(sort)


# CODE
def connect():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect()


# 
# USER GENERATED CONTENT
# 

# Display all items
@app.route('/')
def home():
    cur = g.db.execute('SELECT id, title, description FROM entries ORDER BY id DESC')
    entries = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('item_showcase.html', entries=entries, sort=sort)


# Display particular desktop environment
@app.route('/sort/<family>', methods=['GET', 'POST'])
def display_environment(family):
    title = family
    cur = g.db.execute('SELECT id, title, description FROM entries WHERE family=?', [family])
    entries = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('display_family.html', entries=entries, title=title, sort=sort)


# Display particular theme type
@app.route('/sort/<family>/<genus>', methods=['GET', 'POST'])
def display_genus(family, genus):
    title = [family, genus]
    cur = g.db.execute('SELECT id, title, description FROM entries WHERE family=? AND genus=?', [family, genus])
    entries = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('display_genus.html', entries=entries, title=title)


# Display particular item
@app.route('/sort/<family>/<genus>/<species>', methods=['GET', 'POST'])
def display_species(family, genus, species):
    cur = g.db.execute('SELECT id, title, description FROM entries WHERE family=? AND genus=? AND id=?', [family, genus, species])
    entries = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('display_species.html', entries=entries)


# Add an item
@app.route('/add', methods=['POST'])
def add_item():
    g.db.execute('INSERT INTO entries (title, description) VALUES (?, ?)',[request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was successfully posted.')
    return redirect(url_for('home'))


# Remove an item
@app.route('/remove', methods=['POST'])
def remove_item():
    # really just assign an inactive date
    g.db.execute('UPDATE entries SET inactive = "Yes" WHERE id = ?', item_id)
    g.db.commit()
    flash('Entry was successfully deleted.')
    return redirect(url_for('home'))


# 
# USER REGISTRATION AND SIGN IN AND SIGN OUT
# 


@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if session.get('logged_in'):
        flash('You are already logged in.')    
    elif request.method == 'POST':        
        username = request.form['usr']
        password = request.form['pwd']        
        if request.form['pwd'] != request.form['rpwd']:
            error = 'Passwords do not match.'        
        else:
            try:
                g.db.execute("INSERT INTO users (username, password) VALUES ('%s','%s')" % (username, password))
            except sqlite3.IntegrityError:
                error = 'Username %s is already in database' %username
                g.db.rollback()
            else:
                flash('You have successfully registered.')
                redirect(url_for('home'))
            finally:
                g.db.commit()
    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    # cur = g.db.execute('SELECT id, username, password FROM users WHERE username = "bozo"')
    # printme = [dict(id=row[0], username=row[1], password=row[2]) for row in cur.fetchall()]
    if session.get('logged_in'):
        return redirect(url_for('home'))
    elif request.method == 'POST':
        username = request.form['usr']
        password = request.form['pwd']
       
        cur = g.db.execute('SELECT id, username, password FROM users WHERE username = "%s"' % (username,))
        user = [dict(id=row[0], username=row[1], password=row[2]) for row in cur.fetchall()]

        if user[0]['password'] != request.form['pwd']:
            error = "Incorrect password"
        else:
            session['logged_in'] = True
            return redirect(url_for('home'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))


# 
# ADMINISTRATOR
# 


@app.route('/admin/database', methods=['GET', 'POST'])
def database():
    error = None
    if request.method == 'POST':
        entries = request.form['entries']
        users = request.form['users']  
    cur = g.db.execute('SELECT * FROM users')
    blah = [dict(id=row[0], username=row[1], password=row[2]) for row in cur.fetchall()]

    return render_template('database.html', results=blah, error=error)


if __name__ == '__main__':
    app.run()