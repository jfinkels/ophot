# imports from built-in modules
from contextlib import closing
import os.path
import sqlite3
from uuid import uuid4 as random_uuid

# imports from third party modules
from flask import abort
from flask import Flask
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from werkzeug import secure_filename

# create the application
app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('OPHOT_SETTINGS', silent=True)

def init_db():
    """Initialize the database using the schema specified in the configuration.

    """
    with closing(connect_db()) as db:
        with app.open_resource(app.config['SCHEMA']) as f:
            db.cursor().executescript(f.read())
        db.commit()

def connect_db():
    """Gets a connection to the SQLite database."""
    return sqlite3.connect(app.config['DATABASE'])

# TODO use magic numbers to identify files
def allowed_file(filename):
    return '.' in filename \
        and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

def generate_filename(directory, filename):
    """Generate the path at which to the save a file uploaded by the user.

    For now, this just generates a random UUID (version 4), then appends the
    same extension found from the input filename.
    
    """
    extension = filename.rsplit('.', 1)[1]
    uuid = random_uuid().hex # the string containing just the hex characters
    filename = os.path.join(directory, '{0}.{1}'.format(uuid, extension))
    while os.path.exists(filename):
        uuid = random_uuid().hex
        filename = os.path.join(directory, '{0}.{1}'.format(uuid, extension))
    return filename

@app.before_request
def before_request():
    """Stores the database connection in the db attribute of the g object."""
    g.db = connect_db()

@app.after_request
def after_request(response):
    """Closes the database connection stored in the db attribute of the g
    object.

    The response to the request is returned unchanged.

    """
    g.db.close()
    return response

@app.route('/photos/<category>')
def show_photos(category):
    cursor = g.db.execute('select filename from photos where category == "{0}"'
                          ' order by id asc'.format(category))
    # add the / so that the filenames are relative to the root of the app
    photos = ['/' + row[0] for row in cursor.fetchall()]
    print photos
    return render_template('show_photos.html', photos=photos)

@app.route('/')
def show_splash():
    """Shows the splash page as the root."""
    return render_template('splash.html')

@app.route('/add', methods=['GET', 'POST'])
def add_photos():
    if request.method == 'POST':
        if not session.get('logged_in'):
            abort(401)
        # Multiple files can be gotten from the files attribute on the request
        # object by calling the getlist() method. Check out the werkzeug
        # documentation for info on the FileStorage class and the
        # ImmutableMultiDict class.
        photos = request.files.getlist('photo')
        numphotos = len(photos)
        for photo in photos:
            if allowed_file(photo.filename):
                photo_dir = app.config['PHOTO_DIR']
                if not os.path.exists(photo_dir):
                    os.mkdir(photo_dir)
                filename = generate_filename(app.config['PHOTO_DIR'],
                                             photo.filename)
                photo.save(filename)
                g.db.execute('insert into photos (filename, category) '
                             'values (?, ?)', [filename,
                                               request.form['category']])
                g.db.commit()
        flash(str(numphotos) + ' new photos added.')
        return redirect(url_for('add_photos'))
    elif request.method == 'GET':
        return render_template('add_photos.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] \
                or request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid username or password.'
        else:
            session['logged_in'] = True
            flash('You have successfully logged in.')
            return redirect(url_for('show_splash'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have successfully logged out.')
    return redirect(url_for('show_splash'))

if __name__ == '__main__':
    app.run()

