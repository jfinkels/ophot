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
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flaskext.uploads import UploadSet
from flaskext.uploads import IMAGES
from flaskext.wtf import FileField
from flaskext.wtf import Form
#from flaskext.wtf import FormField
from flaskext.wtf import HiddenField
from flaskext.wtf import SelectField
from flaskext.wtf import TextField
from flaskext.wtf import TextAreaField
from flaskext.wtf.html5 import EmailField
from flaskext.wtf.html5 import IntegerField
from flaskext.wtf.file import file_allowed
from flaskext.wtf.file import file_required
import Image
from werkzeug import secure_filename
#from wtforms.widgets import Input
#from wtforms.validators import Email
from wtforms.validators import NumberRange

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

class SettingsForm(Form):
    """Class which represents the settings form."""
    spacing = IntegerField('Space between photos (in pixels)', validators=[NumberRange(min=0, message='Must be a positive number.')])
    bio = TextAreaField('Bio')
    contact = TextAreaField('Contact info')

    spacing_changed = HiddenField()
    bio_changed = HiddenField()
    contact_changed = HiddenField()


class ChangeSplashPhotoForm(Form):
    """Class which represents the form with which the user can change the
    splash photo.

    """
    photo = FileField('Select new splash photo', validators=[file_required()])#,
    #                  validators=[file_required(),
    #                              file_allowed(splash_photos, 'Images only.')])
    

splash_photos = UploadSet('images', IMAGES)

# create the application and get app configuration from config.py, or a file
app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('OPHOT_SETTINGS', silent=True)

# the first and last name of the photographer
realname = app.config['NAME']

# site-wide configuration which is not necessary for running the app
site_config = ConfigObj(app.config['SETTINGS_FILE'])

if 'BIO' not in site_config:
    site_config['BIO'] = ''
if 'CONTACT' not in site_config:
    site_config['CONTACT'] = ''
if 'SPACING' not in site_config:
    site_config['SPACING'] = app.config['DEFAULT_PHOTO_SPACING']

def _to_html_paragraphs(string):
    """Splits the input string on newlines, then wraps HTML <p> tags around
    each non-empty line.

    """
    return ''.join('<p>{0}</p>'.format(line) for line in string.splitlines()
                   if line)

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

def _get_categories_plus_new():
    """Helper method for the PhotoUploadForm which returns a list of pairs,
    each containing the category ID on the left and the category name on the
    right. The final element of this list is the pair (-1, 'new category...'),
    which is a sentinel value notifying the server that the user wishes to
    create a new category and apply these photos to it.

    Pre-condition: none of the existing categories have an ID of -1.
    """
    return _get_categories().items() + [(-1, 'new category...')]

def _get_categories_plus_new_escaped():
    """Helper method for the PhotoUploadForm which returns a list of pairs,
    each containing the category ID on the left and the category name on the
    right. The final element of this list is the pair (-1,
    'new&nbsp;category...'), which is a sentinel value notifying the server
    that the user wishes to create a new category and apply these photos to it.

    Pre-condition: none of the existing categories have an ID of -1.
    """
    return _get_categories().items() + [(-1, 'new&nbsp;category...')]
    

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

@app.route('/')
def show_splash():
    """Shows the splash page as the root."""
    categories = _get_categories().iteritems()
    bio = _to_html_paragraphs(site_config['BIO'])
    contact = _to_html_paragraphs(site_config['CONTACT'])
    return render_template('splash.html', realname=realname,
                           categories=categories,
                           filename=app.config['SPLASH_PHOTO_FILENAME'],
                           photo_padding=site_config['SPACING'],
                           bio=bio,
                           contact=contact)

@app.route('/change_splash_photo', methods=['GET', 'POST'])
def change_splash_photo():
    """View which on GET requests shows a page containing a form with which the
    user can upload a photo to be the background on the splash page, and on
    POST requests stores the new photo.

    """
    form = ChangeSplashPhotoForm()
    if form.validate_on_submit():
        if not session.get('logged_in'):
            abort(401)
        filename = app.config['SPLASH_PHOTO_FILENAME']
        # TODO same as below; opening and closing a file twice is bad
        request.files['photo'].save(filename)
        im = Image.open(filename)
        if im.size[0] > int(app.config['SPLASH_PHOTO_WIDTH']) \
                or im.size[1] > int(app.config['SPLASH_PHOTO_HEIGHT']):
            im = im.resize((int(app.config['SPLASH_PHOTO_WIDTH']),
                            int(app.config['SPLASH_PHOTO_HEIGHT'])),
                           Image.ANTIALIAS)
            im.save(filename)
        flash('New splash photo uploaded.')
        return redirect(url_for('show_splash'))
    return render_template('change_splash_photo.html', form=form,
                           realname=realname,
                           height=app.config['SPLASH_PHOTO_HEIGHT'],
                           width=app.config['SPLASH_PHOTO_WIDTH'])

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
    # TODO use the "accept" and "required" attributes on the file input field
    # in HTML
    class PhotoUploadForm(Form):
        """Class which represents the photo upload form."""

        # TODO add this validator when it works with multiple files:
        # FileTypeValidator(app.config['ALLOWED_EXTENSIONS'])
        photos = FileField('Select photos to upload',
                           validators=[file_required('Must select a file.')])
        # TODO coerce isn't working
        category = SelectField('Category', coerce=int,
                               choices=_get_categories_plus_new())
    form = PhotoUploadForm()
    if form.validate_on_submit():
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
                # TODO the type coercion is not working for some reason
                categoryid = int(request.form['category'])
                if categoryid == -1:
                    new_category_name = request.form['new-cat-name']
                    if new_category_name in _get_categories().values():
                        # TODO this should be an error message
                        flash('Cannot add new category "{0}" because it'
                              ' already exists.')
                        return redirect(url_for('add_photos'))
                    categoryid = _add_new_category(new_category_name)
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
                # TODO this should be an error message
                flash('{0} is not an acceptable type (must be one of {1}). '
                      'It was not uploaded.'.format(photo.filename,
                      ', '.join(app.config['ALLOWED_EXTENSIONS'])))
        flash('{0} new photos added.'.format(num_photos_added))
        #return redirect(url_for('add_photos'))
    return render_template('add_photos.html', form=form, realname=realname,
                           height=app.config['PHOTO_HEIGHT'])

@app.route('/settings', methods=['GET'])
def edit_settings():
    # create this class so that the form can automatically fill in its values
    # using the values of the attributes of this class
    class Settings(object):
        spacing = site_config['SPACING']
        bio = site_config['BIO']
        contact = site_config['CONTACT']
    # populate the fields of the settings form
    form = SettingsForm(obj=Settings())
    return render_template('edit_settings.html', realname=realname, form=form,
                           categories=_get_categories().iteritems())

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
    return render_template('login.html', error=error, realname=realname)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You have successfully logged out.')
    return redirect(url_for('show_splash'))

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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html', realname=realname), 404

if __name__ == '__main__':
    app.run()
