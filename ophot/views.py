# imports from built-in modules
import os.path
from uuid import uuid4 as random_uuid

# imports from third-party modules
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flaskext.wtf import Form
from flaskext.wtf import FileField
from flaskext.wtf import SelectField
from flaskext.wtf.file import file_required
import Image

# imports from this application
from ophot import _add_new_category
from ophot import _get_categories
from ophot import _get_last_display_position
from ophot import app
from ophot import require_logged_in
from ophot import site_config
from ophot.forms import ChangeSplashPhotoForm
from ophot.forms import SettingsForm
from ophot.queries import Q_ADD_PHOTO

# the first and last name of the photographer
realname = app.config['NAME']


# TODO use mime types or magic numbers to identify files
def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() \
        in app.config['ALLOWED_EXTENSIONS']


def _generate_filename(directory, filename):
    """Generate the path at which to the save a file uploaded by the user.

    For now, this just generates a random UUID (version 4), then appends the
    same extension found from the input filename.

    """
    extension = filename.rsplit('.', 1)[1]
    uuid = random_uuid().hex  # the string containing just the hex characters
    filename = os.path.join(directory, '{0}.{1}'.format(uuid, extension))
    while os.path.exists(filename):
        uuid = random_uuid().hex
        filename = os.path.join(directory, '{0}.{1}'.format(uuid, extension))
    return filename


def _get_categories_plus_new():
    """Helper method for the PhotoUploadForm which returns a list of pairs,
    each containing the category ID on the left and the category name on the
    right. The final element of this list is the pair (-1, 'new category...'),
    which is a sentinel value notifying the server that the user wishes to
    create a new category and apply these photos to it.

    Pre-condition: none of the existing categories have an ID of -1.
    """
    return _get_categories().items() + [(-1, 'new category...')]


def _to_html_paragraphs(string):
    """Splits the input string on newlines, then wraps HTML <p> tags around
    each non-empty line.

    """
    return ''.join('<p>{0}</p>'.format(line) for line in string.splitlines()
                   if line)


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
        require_logged_in()
        filename = os.path.join(app.config['BASE_DIR'],
                                app.config['SPLASH_PHOTO_FILENAME'])
        # TODO see comment in add_photos
        request.files['photo'].save(filename)
        im = Image.open(filename)
        format = im.format
        if im.size[0] > int(app.config['SPLASH_PHOTO_WIDTH']) \
                or im.size[1] > int(app.config['SPLASH_PHOTO_HEIGHT']):
            im = im.resize((int(app.config['SPLASH_PHOTO_WIDTH']),
                            int(app.config['SPLASH_PHOTO_HEIGHT'])),
                           Image.ANTIALIAS)
            im.save(filename, format)
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
        require_logged_in()
        # Multiple files can be gotten from the files attribute on the request
        # object by calling the getlist() method. Check out the werkzeug
        # documentation for info on the FileStorage class and the
        # ImmutableMultiDict class. We would otherwise use the Flask-WTF Form
        # class to access our files, but Flask-WTF does not allow us to access
        # multiple files.
        photos = request.files.getlist('photos')
        num_photos_added = 0
        for photo in photos:
            if _allowed_file(photo.filename):
                photo_dir = os.path.join(app.config['BASE_DIR'],
                                         app.config['PHOTO_DIR'])
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
                filename = _generate_filename(app.config['PHOTO_DIR'],
                                              photo.filename)
                # HACK long_filename is needed for using python to operate on
                # files in the filesystem. the shorter filename is needed for
                # the webpage to correctly link to image sources
                long_filename = os.path.join(app.config['BASE_DIR'], filename)
                # TODO inefficient to read and write the file so many times,
                # but using the file descriptor instead does not seem to save
                # the changes we make on the "im.save()" call below
                photo.save(long_filename)
                im = Image.open(long_filename)
                format = im.format
                if im.size[1] > app.config['PHOTO_HEIGHT']:
                    wdth = im.size[0] * app.config['PHOTO_HEIGHT'] / im.size[1]
                    im = im.resize((wdth, app.config['PHOTO_HEIGHT']))
                    im.save(long_filename, format)
                g.db.execute(Q_ADD_PHOTO, [filename, categoryid, position])
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
def settings():
    # create this class so that the form can automatically fill in its values
    # using the values of the attributes of this class
    class Settings(object):
        spacing = site_config['SPACING']
        bio = site_config['BIO']
        contact = site_config['CONTACT']
    # populate the fields of the settings form
    form = SettingsForm(obj=Settings())
    return render_template('settings.html', realname=realname, form=form,
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


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html', realname=realname), 404


@app.errorhandler(403)
def forbidden(error):
    return render_template('forbidden.html', realname=realname), 403
