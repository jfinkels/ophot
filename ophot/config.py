"""This module contains configuration variables for the Flask application."""

# The set of extensions which the user is allowed to upload.
ALLOWED_EXTENSIONS = set(('png', 'jpg', 'jpeg'))

# Never run a production server with DEBUG mode enabled.
DEBUG = False

# This is the location to which uploaded photos will be stored (relative to the
# directory containing the application).
PHOTO_DIR = 'static/photos/'

# This is the path to the splash photo. If the user changes the splash photo
# using the web interface, this photo will be overwritten with the image file
# which the user uploads.
SPLASH_PHOTO_FILENAME = PHOTO_DIR + 'splash.jpg'

# These are the dimensions (in pixels) to which photos uploaded to be the
# background of the splash page will be resized (if necessary). NOTE: these
# dimensions should probably be the same size as the <div> element which
# contains the image! You can see that in the static/style.css file under
# "div#splash".
SPLASH_PHOTO_WIDTH = 800
SPLASH_PHOTO_HEIGHT = 535

# The height to which uploaded photos will be scaled so that when they are
# displayed, they will be of uniform height.
PHOTO_HEIGHT = 440

# The number of pixels of blank space to leave between each photo when
# displaying photos in a row.
DEFAULT_PHOTO_SPACING = 10

# This is the location of the database schema (relative to the directory from
# which the "reset-db.sh" script is run, which is the top level directory of
# this application).
SCHEMA = 'ophot/schema.sql'

# The base directory for the application. When debugging this application by
# running, for example the "runserver.py" script, this should be 'ophot', since
# the script runs a server in the top level directory of the application. When
# deploying this application as a WSGI application, this should be
# 'ophot/ophot', because the server runs outside of the top level directory of
# this application..
BASE_DIR = 'ophot'

# The location (relative to the directory from which the server is run) to
# store the database for photos.
DATABASE = BASE_DIR + '/db/ophot.db'

# The location of the file which stores the general, site-wide configuration
# settings (like spacing between photos, biography and contact info).
SETTINGS_FILE = BASE_DIR + '/db/settings'

# The location of the file to which warnings and errors will be logged.
LOGFILE = BASE_DIR + '/db/ophot.log'

# A list of recipients to whom emails will be sent when the application
# encounters an error.
ERROR_MAIL_RECIPIENTS = ['webmaster@example.com']

# The subject line for messages sent to the ERROR_MAIL_RECIPIENTS when the
# application encounters an error.
ERROR_MAIL_SUBJECT = 'Ophot failure'

###########################################
# Add to or modify each field below here. #
###########################################

# Change this to the domain on which this application runs. For now, this is
# just used for generating email addresses.
DOMAIN_NAME = "example.com"

# Uncomment this and add a secret key to authenticate sessions with a logged in
# user.  To generate a 24 byte secret key with python, do:
#
# >>> import os
# >>> os.urandom(24)
#
# Then just copy the resulting string here.
#SECRET_KEY = ''

# Fill in the username and password for the user that will manage photos.
#USERNAME = ''
#PASSWORD = ''

# Add the name that you wish to appear across the site.
NAME = 'Example Exampleson'

# Add the email address which the user should contact when he or she wishes to
# purchase a print.
PURCHASE_EMAIL = 'example@example.com'
