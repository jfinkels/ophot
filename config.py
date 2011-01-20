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

#############################################
# Add or modify all information below here. #
#############################################

# Generate a secret key to authenticate sessions with a logged in user.
#SECRET_KEY = ''

# Fill in the username and password for the user that will manage photos.
#USERNAME = ''
#PASSWORD = ''

# Add your contact information.
EMAIL = 'example@example.com'
NAME = 'Examply McExample'
PHONE = '555-5555'
