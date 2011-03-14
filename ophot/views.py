# imports from third-party modules
from flask import render_template

# imports from this application
from ophot import _get_categories
from ophot import app
from ophot import site_config

# the first and last name of the photographer
realname = app.config['NAME']

def _get_categories_plus_new():
    """Helper method for the PhotoUploadForm which returns a list of pairs,
    each containing the category ID on the left and the category name on the
    right. The final element of this list is the pair (-1, 'new category...'),
    which is a sentinel value notifying the server that the user wishes to
    create a new category and apply these photos to it.

    Pre-condition: none of the existing categories have an ID of -1.
    """
    return _get_categories().items() + [(-1, 'new category...')]

# def _get_categories_plus_new_escaped():
#     """Helper method for the PhotoUploadForm which returns a list of pairs,
#     each containing the category ID on the left and the category name on the
#     right. The final element of this list is the pair (-1,
#     'new&nbsp;category...'), which is a sentinel value notifying the server
#     that the user wishes to create a new category and apply these photos to it.

#     Pre-condition: none of the existing categories have an ID of -1.
#     """
#     return _get_categories().items() + [(-1, 'new&nbsp;category...')]
    
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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html', realname=realname), 404

