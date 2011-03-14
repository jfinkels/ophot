# imports from built-in modules
from contextlib import closing
import os.path
import sqlite3
from uuid import uuid4 as random_uuid

# imports from third party modules
from configobj import ConfigObj
from flask import abort
from flask import Flask
from flask import flash
from flask import g
from flask import jsonify
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flaskext.uploads import UploadSet
from flaskext.uploads import IMAGES
from flaskext.wtf import FileField
from flaskext.wtf import Form
from flaskext.wtf import SelectField
from flaskext.wtf import TextField
from flaskext.wtf import TextAreaField
from flaskext.wtf.html5 import IntegerField
#from flaskext.wtf.file import file_allowed
from flaskext.wtf.file import file_required
import Image
from wtforms.validators import NumberRange


class SettingsForm(Form):
    """Class which represents the settings form."""
    spacing = IntegerField('Space between photos (in pixels)', validators=[NumberRange(min=0, message='Must be a positive number.')])
    bio = TextAreaField('Bio')
    contact = TextAreaField('Contact info')


class ChangeSplashPhotoForm(Form):
    """Class which represents the form with which the user can change the
    splash photo.

    """
    # also want to add "file_allowed(splash_photos, 'Images only.')" here
    photo = FileField('Select new splash photo', validators=[file_required()])
    

splash_photos = UploadSet('images', IMAGES)

# create the application and get app configuration from config.py, or a file
app = Flask(__name__)
app.config.from_object('ophot.config')
app.config.from_envvar('OPHOT_SETTINGS', silent=True)

# site-wide configuration which is not necessary for running the app
site_config = ConfigObj(app.config['SETTINGS_FILE'])
if 'BIO' not in site_config:
    site_config['BIO'] = ''
if 'CONTACT' not in site_config:
    site_config['CONTACT'] = ''
if 'SPACING' not in site_config:
    site_config['SPACING'] = app.config['DEFAULT_PHOTO_SPACING']

def _add_new_category(categoryname):
    """Creates a new category in the database with the specified *categoryname*
    and returns its ID number.

    """
    g.db.execute('insert into category (categoryname) values (?)',
                 [categoryname])
    g.db.commit()
    # get the ID of the category that we just inserted
    return g.db.execute('select categoryid from category where'
                        ' categoryname == "{0}"'.format(categoryname)).fetchone()[0]

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

@app.route('/_get_photos', methods=['GET'])
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

@app.route('/_change_category', methods=['GET'])
def change_category():
    """Ajax method which changes the category of a photo.

    Request arguments are *photoid*, an integer which is the ID of the photo to
    change, and *categoryid*, an integer which is the ID of the category to
    which the photo will be moved. If *categoryid* is equal to -1, this method
    will check for the *categoryname* request argument, create the category
    with that name, and move the photo with the specified ID to that category.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the category was successfully changed, *photoid* to the ID of the photo,
    and *categoryid* to the ID of the category.

    If the photo is being changed to the same category, this method will change
    its display order position to be last.
    """
    if not session.get('logged_in'):
        abort(401)
    categoryid = request.args.get('categoryid')
    if int(categoryid) == -1:
        categoryname = request.args.get('categoryname')
        if categoryname is None or len(categoryname) == 0:
            return jsonify(changed=False, photoid=photoid,
                           categoryid=categoryid, reason='No name received.')
        categoryid = _add_new_category(categoryname)
    photoid = request.args.get('photoid')
    position = _get_last_display_position(categoryid)
    if position is None:
        position = 1
    g.db.execute('update photo set photocategory={0},photodisplayposition={1}'
                 ' where photoid={2}'.format(categoryid, position, photoid))
    g.db.commit()
    return jsonify(changed=True, photoid=photoid, categoryid=categoryid)

@app.route('/_get_categories', methods=['GET'])
def get_categories():
    """Ajax method which returns a JSON object storing an array of categories
    in alphabetical (lexicographical) order.

    """
    return jsonify(_get_categories().iteritems())


@app.route('/_change_category_name', methods=['GET'])
def change_category_name():
    """Ajax method which updates the name of the category with the specified ID
    number to the specified new name.

    Request arguments are *categoryid*, an integer which is the ID of the
    category whose name will be changed, and *categoryname*, the new name for
    the category.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the category was successfully changed, *categoryid* to the ID of the
    category, and *categoryname* to the new name of the category.
    """
    # TODO move these two lines into a function
    if not session.get('logged_in'):
        abort(401)
    categoryid = request.args.get('categoryid')
    categoryname = request.args.get('categoryname')
    g.db.execute('update category set categoryname="{0}" where categoryid={1}'
                 .format(categoryname, categoryid))

    g.db.commit()
    return jsonify(changed=True)

@app.route('/_update_personal', methods=['GET'])
def update_personal():
    """Ajax method which changes either bio information or contact information.

    The request arguments are *name*, which must be either "bio" or "contact",
    and *value* which is the new value for the personal information.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the info was successfully changed.

    """
    if not session.get('logged_in'):
        abort(401)
    name = request.args.get('name').upper()
    value = request.args.get('value')
    if name == 'BIO' or name == 'CONTACT':
        site_config[name] = value
        site_config.write()
    else:
        # TODO log this as an error
        pass
    return jsonify(changed=True)

# TODO POST method doesn't seem to be working
@app.route('/_change_spacing', methods=['GET'])
def change_spacing():
    """Ajax method which changes the value of the spacing between photos on the
    photo display page.

    The only request argument is *spacing*, the number of pixels between
    photos.

    Returns a JSON object mapping *changed* to a boolean representing whether
    the spacing was successfully changed.

    """
    if not session.get('logged_in'):
        abort(401)
    # TODO use a validator for configobj
    site_config['SPACING'] = int(request.args.get('spacing'))
    site_config.write()
    return jsonify(changed=True)

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

import ophot.views

if __name__ == '__main__':
    app.run()
