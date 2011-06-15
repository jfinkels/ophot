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
"""Unit tests for the ophot module."""
# imports from built-in modules
import os
import sqlite3
import tempfile
import unittest
#import uuid

# imports from third party modules
#from werkzeug.datastructures import FileStorage
#from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import Unauthorized

# imports from this application
from ophot import add_new_category
from ophot import app
from ophot import after_request
from ophot import before_request
from ophot import connect_db
from ophot import init_db
from ophot import get_categories
from ophot import get_last_display_position
from ophot import require_logged_in
from ophot import select_single


class temp_photos(object):
    """Context manager (for use in a "with" statement) which creates temporary
    files representing photos, connects to the database, adds photos to it,
    then on exit removes the files.

    """
    def __init__(self):
        """This method does nothing."""
        pass

    def __enter__(self):
        """Creates temporary photos and adds them to the database.

        Specifically, two photos will be added to category with ID 1, one photo
        will be added to category with ID 2, and no photos will be added to
        category with ID 3.

        """
        # mkstemp() returns a 2-tuple: (file_descriptor, filename)
        self.photos = [tempfile.mkstemp() for i in range(3)]
        self.conn = connect_db()
        self.conn.execute('insert into photo (photofilename,'
                          ' photocategory, photodisplayposition)'
                          ' values (?, ?, ?)',
                          [self.photos[0][1], '1', '1'])
        self.conn.execute('insert into photo (photofilename,'
                          ' photocategory, photodisplayposition)'
                          ' values (?, ?, ?)',
                          [self.photos[1][1], '1', '2'])
        self.conn.execute('insert into photo (photofilename,'
                          ' photocategory, photodisplayposition)'
                          ' values (?, ?, ?)',
                          [self.photos[2][1], '2', '1'])
        self.conn.commit()

    def __exit__(self, exception_type, exception_value, traceback):
        """Unlinks the temporary files and closes the database connection."""
        self.conn.close()
        for f in self.photos:
            os.unlink(f[1])


class OphotTestCase(unittest.TestCase):
    """Test class for the __init__ module in the ophot package."""

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

    def test_add_new_category(self):
        """Test for adding a new category to the database."""
        with app.test_request_context('/'):
            before_request()
            categories = get_categories()
            new_id = add_new_category('foobar')
            new_categories = get_categories()
            self.assertNotIn(new_id, categories)
            self.assertEqual(max(categories) + 1, new_id)
            self.assertIn('foobar', new_categories.values())

    def test_connect_db(self):
        """Tests that the ophot module correctly connects to a database."""
        try:
            conn = connect_db()
            cursor = conn.execute('select *  from photo')
            self.assertTrue(len(cursor.fetchall()) == 0)
            cursor = conn.execute('select * from category')
            rows = cursor.fetchall()
            self.assertTrue(rows[0][1] == 'landscape')
            self.assertTrue(rows[1][1] == 'personal')
            self.assertTrue(rows[2][1] == 'portrait')
        finally:
            conn.close()

    def test_get_categories(self):
        """Test for getting categories with their ID numbers."""
        with app.test_request_context('/'):
            before_request()
            categories = get_categories()
            self.assertIn((1, 'landscape'), categories.items())
            self.assertIn((2, 'personal'), categories.items())
            self.assertIn((3, 'portrait'), categories.items())

    def test_get_last_display_position(self):
        """Test for getting the display position of the photo which is to be
        displayed last.

        """
        with app.test_request_context('/'):
            before_request()
            with temp_photos():
                x = get_last_display_position(1)
                self.assertEqual(2, get_last_display_position(1))
                self.assertEqual(1, get_last_display_position(2))
                self.assertEqual(None, get_last_display_position(3))

    def test_init_db(self):
        """Tests that the ophot module correctly initializes a database."""
        conn = None
        try:
            conn = sqlite3.connect(app.config['DATABASE'])
            cursor = conn.execute('select *  from photo')
            self.assertTrue(len(cursor.fetchall()) == 0)
            cursor = conn.execute('select * from category')
            rows = cursor.fetchall()
            self.assertTrue(rows[0][1] == 'landscape')
            self.assertTrue(rows[1][1] == 'personal')
            self.assertTrue(rows[2][1] == 'portrait')
        finally:
            if conn is not None:
                conn.close()

    def test_login(self):
        result = self._login()
        self.assertTrue('You have successfully logged in.' in result.data)
        result = self._logout()
        self.assertTrue('You have successfully logged out.' in result.data)
        result = self._login(username='bogus')
        self.assertTrue('Invalid username or password.' in result.data)
        result = self._login(password='bogus')
        self.assertTrue('Invalid username or password.' in result.data)

    def test_logout(self):
        result = self._login()
        self.assertTrue('You have successfully logged in.' in result.data)
        result = self._logout()
        self.assertTrue('You have successfully logged out.' in result.data)

    @unittest.skip('The flask.session object does not seem to work here.')
    def test_require_logged_in(self):
        """Test for requiring that the user is marked as logged in on the
        session.

        """
        with app.test_request_context('/'):
            self.assertRaisesRegexp(Unauthorized, '401', require_logged_in)
            self._login()
            # here we expect no exception
            require_logged_in()

    def test_select_single(self):
        """Tests that the select_single function returns a single field from
        the first matched row of a query.

        """
        with app.test_request_context('/'):
            before_request()
            with temp_photos():
                position = select_single('select photodisplayposition from'
                                         ' photo where photocategory=2')
                self.assertEqual(1, position)
                position = select_single('select photodisplayposition from'
                                         ' photo where photocategory=3')
                self.assertIsNone(None, position)
