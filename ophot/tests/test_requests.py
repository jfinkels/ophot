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
"""Unit tests for the requests module."""
import json
import os
import tempfile
import unittest

from flask import request

from ophot import app
from ophot import before_request
from ophot import init_db
from ophot.requests import add_category
from ophot.requests import change_category
from ophot.requests import change_category_name
from ophot.requests import change_spacing
from ophot.requests import delete_category
from ophot.requests import delete_photo
from ophot.requests import get_categories
from ophot.requests import get_photos
from ophot.requests import swap_display_positions
from ophot.requests import update_personal

def query_url(base, **kw):
    query = '&'.join('{0[0]}={0[1]}'.format(item) for item in kw.iteritems())
    return '{0}?{1}'.format(base, query)

class RequestsTestCase(unittest.TestCase):
    """Test class for the requests module."""

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
        s = tempfile.mkstemp()
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        self.app = app.test_client()
        init_db()

    def tearDown(self):
        """Closes and deletes the database."""
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def test_add_category(self):
        """Test for adding a category."""
        self._login()
        result = self.app.get(query_url('/_add_category', categoryname='foo'))
        result = json.loads(result.data)
        self.assertEqual(True, result['added'])
        self.assertEqual(4, result['categoryid'])
        self.assertEqual('foo', result['categoryname'])
