# Copyright 2011 Jeffrey Finkelstein
#
# This file is part of Ophot.
#
# Ophot is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ophot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Ophot.  If not, see <http://www.gnu.org/licenses/>.
"""Provides routes which are viewed as webpages by the user."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import json
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
#from flaskext.uploads import UploadSet
#from flaskext.uploads import IMAGES
from flaskext.wtf import Form
from flaskext.wtf import FileField
from flaskext.wtf import SelectField
#from flaskext.wtf.file import file_allowed
from flaskext.wtf.file import file_required
import Image

# imports from this application
from .app import app
from .app import site_config
from .categories import get_categories
from .helpers import get_last_display_position
from .helpers import require_logged_in
from .queries import Q_ADD_PHOTO

# the first and last name of the photographer
realname = app.config['NAME']
# the email to display to users for purchasing a photo
purchase_email = app.config['PURCHASE_EMAIL']


#splash_photos = UploadSet('images', IMAGES)
class ChangeSplashPhotoForm(Form):
    """Class which represents the form with which the user can change the
    splash photo.

    """
    # also want to add "file_allowed(splash_photos, 'Images only.')" here
    photo = FileField('Select new splash photo', validators=[file_required()])


# TODO use mime types or magic numbers to identify files
def _allowed_file(filename):
    """Returns True if and only if the specified filename has an allowed file
    extension, which are defined in the application configuration.

    """
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


def _get_category_names():
    """Returns a list containing the names of each of the categories in the
    database.

    """
    categories = json.loads(get_categories().data)['items']
    return (category['name'] for category in categories)


def _get_categories_plus_new():
    """Helper method for the PhotoUploadForm which returns a list of pairs,
    each containing the category ID on the left and the category name on the
    right. The final element of this list is the pair (-1, 'new category...'),
    which is a sentinel value notifying the server that the user wishes to
    create a new category and apply these photos to it.

    Pre-condition: none of the existing categories have an ID of -1.
    """
    categories = json.loads(get_categories().data)['items']
    categories = [(cat['id'], cat['name']) for cat in categories]
    categories.append((-1, 'new category...'))
    return categories


def _to_html_paragraphs(string):
    """Splits the input string on newlines, then wraps HTML <p> tags around
    each non-empty line.

    """
    return ''.join('<p>{0}</p>'.format(line) for line in string.splitlines()
                   if line)


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
                    if new_category_name in _get_category_names():
                        # TODO this should be an error message
                        flash('Cannot add new category "{0}" because it'
                              ' already exists.')
                        return redirect(url_for('add_photos'))
                    response = create_category(new_category_name)
                    categoryid = json.loads(response.data)['id']
                position = (get_last_display_position(categoryid) or 0) + 1
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
                image_format = im.format
                if im.size[1] > app.config['PHOTO_HEIGHT']:
                    wdth = (im.size[0] * app.config['PHOTO_HEIGHT'])
                    # recall: "a // b" is equivalent to "floor(a / b)"
                    wdth //= im.size[1]
                    im = im.resize((wdth, app.config['PHOTO_HEIGHT']))
                    im.save(long_filename, image_format)
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
        image_format = im.format
        if im.size[0] > int(app.config['SPLASH_PHOTO_WIDTH']) \
                or im.size[1] > int(app.config['SPLASH_PHOTO_HEIGHT']):
            im = im.resize((int(app.config['SPLASH_PHOTO_WIDTH']),
                            int(app.config['SPLASH_PHOTO_HEIGHT'])),
                           Image.ANTIALIAS)
            im.save(filename, image_format)
        flash('New splash photo uploaded.')
        return redirect(url_for('show_splash'))
    return render_template('change_splash_photo.html', form=form,
                           realname=realname,
                           height=app.config['SPLASH_PHOTO_HEIGHT'],
                           width=app.config['SPLASH_PHOTO_WIDTH'])


# TODO use the error parameter
@app.errorhandler(403)
def forbidden(error):
    """Renders the template for an HTML error status 403 (Forbidden)."""
    return render_template('forbidden.html', realname=realname), 403


# TODO use Flask-CSRF?
@app.route('/login', methods=['GET', 'POST'])
def login():
    """On a GET request, renders the login template, and on a POST request,
    sets the 'logged_in' property of the session variable to be True after
    checking the POSTed credentials.

    """
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
    """Unsets the 'logged_in' property of the session variable, then redirects
    to the splash page.

    """
    session.pop('logged_in', None)
    flash('You have successfully logged out.')
    return redirect(url_for('show_splash'))


# TODO use the error parameter
@app.errorhandler(404)
def page_not_found(error):
    """Renders the template for an HTML error status 404 (Not Found)."""
    return render_template('page_not_found.html', realname=realname), 404


@app.route('/settings', methods=['GET'])
def settings():
    """Renders the edit settings template."""
    categories = json.loads(get_categories().data)['items']
    return render_template('settings.html', realname=realname,
                           categories=categories,
                           bio=site_config['BIO'],
                           contact=site_config['CONTACT'],
                           spacing=site_config['SPACING'])


@app.route('/')
def show_splash():
    """Shows the splash page as the root."""
    categories = json.loads(get_categories().data)['items']
    bio = _to_html_paragraphs(site_config['BIO'])
    contact = _to_html_paragraphs(site_config['CONTACT'])
    return render_template('splash.html', realname=realname,
                           categories=categories,
                           filename=app.config['SPLASH_PHOTO_FILENAME'],
                           photo_padding=site_config['SPACING'],
                           bio=bio, purchase_email=purchase_email,
                           contact=contact)


# TODO use the error parameter
@app.errorhandler(401)
def unauthorized(error):
    """Renders the template for an HTML error status 401 (Unauthorized)."""
    return render_template('unauthorized.html', realname=realname), 401
