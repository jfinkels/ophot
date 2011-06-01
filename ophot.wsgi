# IMPORTANT change the paths below to be the path to the top level directory of
# the application and the path to the activation script for the virtualenv
# environment in which this application will run
PATH_TO_APP = '/var/www/ophot'
PATH_TO_VIRTUALENV = PATH_TO_APP + '/env/bin/activate_this.py'

# add the path to the application to the beginning Python path so that it is
# checked first
import sys
sys.path.insert(0, PATH_TO_APP)

# use a virtualenv environment which has all dependencies installed
activate_this = PATH_TO_VIRTUALENV
execfile(activate_this, dict(__file__=activate_this))

# import the Flask app as the WSGI application
from ophot import app as application
