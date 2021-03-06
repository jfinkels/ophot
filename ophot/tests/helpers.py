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
"""Provides a test suite for all tests for the Ophot package."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import os
import os.path
import tempfile
from unittest import TestCase

# imports from this application
from ..app import app
from ..helpers import connect_db
from ..helpers import init_db


class temp_photos(object):
    """Context manager (for use in a "with" statement) which creates temporary
    files representing photos, connects to the database, adds photos to it,
    then on exit removes the files.

    """
    def __enter__(self):
        """Creates temporary photos and adds them to the database.

        Specifically, two photos will be added to category with ID 1, one photo
        will be added to category with ID 2, and no photos will be added to
        category with ID 3.

        """
        self.conn = connect_db()
        self.conn.execute('insert into photo (photofilename,'
                          ' photocategory, photodisplayposition)'
                          ' values (?, ?, ?)',
                          ['photo1', '1', '2'])
        self.conn.execute('insert into photo (photofilename,'
                          ' photocategory, photodisplayposition)'
                          ' values (?, ?, ?)',
                          ['photo2', '1', '1'])
        self.conn.execute('insert into photo (photofilename,'
                          ' photocategory, photodisplayposition)'
                          ' values (?, ?, ?)',
                          ['photo3', '2', '1'])
        self.conn.commit()

    # TODO why not just put this at the end of enter?
    def __exit__(self, exception_type, exception_value, traceback):
        """Unlinks the temporary files and closes the database connection."""
        self.conn.close()


# HACK this wrapper is required because the Flask test client (which is itself
# a wrapper around the Werkzeug test client) has no "patch()" function. This
# acts as a transparent wrapper which adds that function to the test client.
# class PatchableTestClientWrapper(object):
#     def __init__(self, test_client):
#         self.client = test_client
#     def __getattr__(self, name):
#         return getattr(self.client, name)
#     def patch(self, *args, **kw):
#         kw['method'] = 'PATCH'
#         return self.client.open(*args, **kw)
#    
#
class TestSupport(TestCase):
    """Base class for test cases in other modules in this package which
    provides login and logout functions, and set up and tear down functions.

    """

    def _login(self, username=app.config['USERNAME'],
               password=app.config['PASSWORD']):
        """Makes a POST request to login to the Flask application with the
        specified username and password. If no username and password are
        specified, the ones from the configuration will be used.

        """
        return self.app.post('/login',
                             data={'username': username, 'password': password},
                             follow_redirects=True)

    def _logout(self):
        """Logs out from the current application."""
        return self.app.get('/logout', follow_redirects=True)

    def setUp(self):
        """Connects the Flask application to a temporary database and creates a
        client for testing.

        """
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        #self.app = PatchableTestClientWrapper(app.test_client())
        self.app = app.test_client()
        # HACK when run from "python setup.py test", the path to the database
        # schema used to initialize the database has one too many "ophot/"
        app.config['SCHEMA'] = os.path.basename(app.config['SCHEMA'])
        init_db()

    def tearDown(self):
        """Closes and deletes the database."""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
