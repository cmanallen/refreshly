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
    "gnome": ["gnome-shell", "gtk", "gdm"],
    "kde": ["plasma", "qt", "kdm"],
    "xfce": ["gtk"],
    "elementary": ["pantheon", "gtk", "ldm", "icons"],
    "mint": ["cinnamon", "gtk", "mdm"],
}


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
    cur = g.db.execute('SELECT id, title, description, family, genus FROM items ORDER BY id DESC')
    entries = [dict(id=row[0], title=row[1], description=row[2], family=row[3], genus=row[4]) for row in cur.fetchall()]
    return render_template('item_showcase.html', entries=entries, sort=sort)


# Display particular desktop environment
@app.route('/sort/<family>', methods=['GET', 'POST'])
def display_environment(family):
    if family not in sort:
        abort(404)
    title = family
    cur = g.db.execute('SELECT id, title, description FROM items WHERE family=?', [family])
    entries = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('display_family.html', entries=entries, title=title, sort=sort)


# Display particular theme type
@app.route('/sort/<family>/<genus>', methods=['GET', 'POST'])
def display_genus(family, genus):
    if family not in sort:
        abort(404)
    if genus not in sort[family]:
        abort(404)
    title = [family, genus]
    cur = g.db.execute('SELECT id, title, description FROM items WHERE family=? AND genus=?', [family, genus])
    entries = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('display_genus.html', entries=entries, title=title)


# Display particular item
@app.route('/sort/<family>/<genus>/<species>', methods=['GET', 'POST'])
def display_species(family, genus, species):
    if family not in sort:
        abort(404)
    if genus not in sort[family]:
        abort(404)
    cur = g.db.execute('SELECT id, title, description FROM items WHERE family=? AND genus=? AND id=?', [family, genus, species])
    entries = [dict(id=row[0], title=row[1], description=row[2]) for row in cur.fetchall()]
    return render_template('display_species.html', entries=entries)


# Add an item
@app.route('/', methods=['POST'])
def add_item():
    g.db.execute('INSERT INTO items (title, description, family, genus) VALUES (?, ?, ?, ?)',[request.form['title'], request.form['text'], request.form['family'], request.form['genus']])
    g.db.commit()
    flash('New entry was successfully posted.')
    return redirect(url_for('home'))


# Remove an item
@app.route('/remove', methods=['POST'])
def remove_item():
    # really just assign an inactive date
    g.db.execute('UPDATE items SET inactive = "Yes" WHERE id = ?', item_id)
    g.db.commit()
    flash('Entry was successfully deleted.')
    return redirect(url_for('home'))


#
# USER AREA
#

@app.route('/profile/<name>', methods=['GET', 'POST'])
def user_profile(name):
    username = name
    cur = g.db.execute('SELECT id, username FROM users WHERE id = ?', [name])
    user = [dict(id=row[0], username=row[1]) for row in cur.fetchall()]
    return render_template('profile.html', user=user, username=username)

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
                error = 'Username %s is taken!' %username
                g.db.rollback()
            else:
                flash('You have successfully registered.')
                return redirect(url_for('home'))
            finally:
                g.db.commit()
    return render_template('register.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
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
    cur = g.db.execute('SELECT * FROM items')
    blah = [dict(id=row[0], title=row[1], description=row[2], family=row[3], genus=row[4]) for row in cur.fetchall()]

    return render_template('database.html', results=blah, error=error)


if __name__ == '__main__':
    app.run()