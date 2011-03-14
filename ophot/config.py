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

# This is the location (relative to the directory from which the server is run)
# of the database schema.
SCHEMA = 'ophot/schema.sql'

# The location (relative to the directory from which the server is run) to
# store the database for photos.
DATABASE = 'ophot/db/ophot.db'

# The location of the file which stores the general, site-wide configuration
# settings (like spacing between photos, biography and contact info).
SETTINGS_FILE = 'ophot/db/settings'

###########################################
# Add to or modify each field below here. #
###########################################

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
