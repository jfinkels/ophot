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
