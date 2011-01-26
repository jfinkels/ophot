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
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flaskext.wtf import Form
from flaskext.wtf import FileField
#from flaskext.wtf import Required
from flaskext.wtf import SelectField
#from flaskext.wtf import ValidationError
import Image
#from werkzeug import secure_filename

# class FileTypeValidator(object):
#     def __init__(self, extensions, message=None):
#         """Creates a validator which checks that a given filename has an
#         extension in the specified set of extensions.

#         If not, a ValidationError will be raised with the specified message.

#         """
#         self.extensions = extensions
#         if not message:
#             message = 'File type not allowed (must be one of {0})'.format(extensions)
#         self.message = message

#     def __call__(self, form, field):
#         """Validates the filename against the set of allowed file type
#         extensions specified in the constructor of this class.

#         """
#         raise ValidationError('unimplemented')

# create the application
app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('OPHOT_SETTINGS', silent=True)

name = app.config['NAME']

def _get_categories():
    """Helper method which returns a map from category ID to category name,
    sorted in alphabetical (lexicographical) order by category name.

    """
    cursor = g.db.execute('select categoryid, categoryname from category'
                          ' order by categoryname asc')
    return dict([(row[0], row[1]) for row in cursor.fetchall()])

def _get_last_display_position(categoryid):
    # sometimes returns None
    return g.db.execute('select max(photodisplayposition) from photo where'
                        ' photocategory == "{0}"'
                        .format(categoryid)).fetchone()[0]


def update_categories(form):
    """Updates the choices in the category SelectField of the specified form
    with the categories selected from the database.
    
    """
    form.category.choices = _get_categories().items()

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

# TODO use mime types or magic numbers to identify files
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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

# def scaled_image(filename, new_height):
#     """Returns the image at the specified filename scaled to the specified
#     height, maintaining correct aspect ratio.

#     """
#     im = Image.open(filename)
#     new_width = im.size[0] * height / im.size[1]
#     im.resize((new_width, new_height))
#     return im

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

# @app.route('/photos/<category>')
# def show_photos(category):
#     cursor = g.db.execute('select filename from photos where category == "{0}"'
#                           ' order by id asc'.format(category))
#     # add the / so that the filenames are relative to the root of the app
#     photos = ['/' + row[0] for row in cursor.fetchall()]
#     return render_template('show_photos.html', photos=photos,
#                            num_photos=len(photos), name=name)

@app.route('/')
def show_splash():
    """Shows the splash page as the root."""
    categories = _get_categories().iteritems()
    return render_template('splash.html', name=name, email=app.config['EMAIL'],
                           phone=app.config['PHONE'], categories=categories)

@app.route('/add', methods=['GET', 'POST'])
def add_photos():
    """View which on GET requests shows a page containing a form with which the
    user can upload multiple photos with a single category, and on POST
    requests stores photos on the filesystem and adds their filenames to the
    database.

    """

    # HACK we need to create this class anew each time we need it because the
    # category class variable depends on the categories read from the database,
    # which may change over time
    class PhotoUploadForm(Form):
        """Class which represents the photo upload form."""

        # TODO add this validator when it works with multiple files:
        # FileTypeValidator(app.config['ALLOWED_EXTENSIONS'])
        photos = FileField('Select photos to upload')
        category = SelectField('Category', coerce=int,
                               choices=_get_categories().items())
    form = PhotoUploadForm(request.form)
    if request.method == 'POST' and form.validate():
        if not session.get('logged_in'):
            abort(401)
        # Multiple files can be gotten from the files attribute on the request
        # object by calling the getlist() method. Check out the werkzeug
        # documentation for info on the FileStorage class and the
        # ImmutableMultiDict class. We would otherwise use the Flask-WTF Form
        # class to access our files, but Flask-WTF does not allow us to access
        # multiple files.
        photos = request.files.getlist('photos')
        num_photos_added = 0
        for photo in photos:
            if allowed_file(photo.filename):
                photo_dir = app.config['PHOTO_DIR']
                if not os.path.exists(photo_dir):
                    os.mkdir(photo_dir)
                categoryid = request.form['category']
                result = _get_last_display_position(categoryid)
                if _get_last_display_position(categoryid) is None:
                    position = 1
                else:
                    position = result + 1
                filename = generate_filename(app.config['PHOTO_DIR'],
                                             photo.filename)
                # TODO writing then reading the same file is slow. To fix this:
                # first open a file, then pass the filedescriptor to photo.save
                # and image.open (specify the type for image.open)
                photo.save(filename)
                im = Image.open(filename)
                if im.size[1] > app.config['PHOTO_HEIGHT']:
                    wdth = im.size[0] * app.config['PHOTO_HEIGHT'] / im.size[1]
                    im = im.resize((wdth, app.config['PHOTO_HEIGHT']))
                    im.save(filename)
                g.db.execute('insert into photo (photofilename, photocategory,'
                             ' photodisplayposition) values (?, ?, ?)',
                             [filename, categoryid, position])
                g.db.commit()
                num_photos_added += 1
            else:
                flash('{0} is not an acceptable type (must be one of {1}). '
                      'It was not uploaded.'.format(photo.filename,
                      ', '.join(app.config['ALLOWED_EXTENSIONS'])))
        flash('{0} new photos added.'.format(num_photos_added))
        return redirect(url_for('add_photos'))
    return render_template('add_photos.html', form=form, name=name,
                           height=app.config['PHOTO_HEIGHT'])

# TODO use Flask-CSRF?
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
    return render_template('login.html', error=error, name=name)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have successfully logged out.')
    return redirect(url_for('show_splash'))

@app.route('/_get_photos')
def get_photos():
    """Ajax method which returns a JSON object which is a map from photoid to
    filenames of photos in the category specified in the request argument
    *categoryid*.

    """
    category = request.args.get('categoryid')
    cursor = g.db.execute('select photoid, photofilename from photo'
                          ' where photocategory == "{0}"'
                          ' order by photodisplayposition asc'
                          .format(category))
    # add the / so that the filenames are relative to the root of the app
    photos = dict([(row[0], '/' + row[1]) for row in cursor.fetchall()])
    return jsonify(photos)

# @app.route('/_get_category')
# def get_category():
#     """Ajax method which returns the category of a photo.
    
#     Request arguments are *photoid*, an integer which is the ID of the photo
#     whose category will be returned.
#     """
#     pass

@app.route('/_change_category')
def change_category():
    """Ajax method which changes the category of a photo.

    Request arguments are *photoid*, an integer which is the ID of the photo to
    change, and *categoryid*, an integer which is the ID of the category to
    which the photo will be moved.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the category was successfully changed, *photoid* to the ID of the photo,
    and *categoryid* to the ID of the category.

    If the photo is being changed to the same category, this method will change
    its display order position to be last.
    """
    if not session.get('logged_in'):
        abort(401)
    categoryid = request.args.get('categoryid')
    photoid = request.args.get('photoid')
    position = _get_last_display_position(categoryid)
    if position is None:
        position = 1
    g.db.execute('update photo set photocategory={0},photodisplayposition={1}'
                 ' where photoid={2}'.format(categoryid, position, photoid))
    g.db.commit()
    return jsonify(changed=True, photoid=photoid, categoryid=categoryid)

@app.route('/_get_categories')
def get_categories():
    """Ajax method which returns a JSON object storing an array of categories
    in alphabetical (lexicographical) order.

    """
    return jsonify(_get_categories().iteritems())

@app.route('/delete/<int:photoid>', methods=['DELETE'])
def delete_photo(photoid):
    """Ajax method which deletes the photo with the specified ID number from
    the database, and returns a boolean representing whether the action was
    successful.

    """
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('delete from photo where photoid == {0}'.format(photoid))
    g.db.commit()
    return jsonify(deleted=True, photoid=photoid)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html', name=name), 404

if __name__ == '__main__':
    app.run()
