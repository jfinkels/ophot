# The set of extensions which the user is allowed to upload.
ALLOWED_EXTENSIONS = set(('png', 'jpg', 'jpeg'))

# Never run a production server with DEBUG mode enabled.
DEBUG = False

# This is the location to which uploaded photos will be stored.
PHOTO_DIR = 'static/photos'

# This is the database schema.
SCHEMA = 'schema.sql'

# The location to store the database for photos.
DATABASE = 'db/ophot.db'

###########################################
# Add to or modify each field below here. #
###########################################

# Generate a secret key to authenticate sessions with a logged in user.
# To generate a 24 byte secret key with python, do:
#
# >>> import os
# >>> os.urandom(24)
#
# Then just copy the resulting string here.
#SECRET_KEY = ''

# Fill in the username and password for the user that will manage photos.
#USERNAME = ''
#PASSWORD = ''

# Add your contact information.
EMAIL = 'example@example.com'
NAME = 'Examply McExample'
PHONE = '555-5555'
