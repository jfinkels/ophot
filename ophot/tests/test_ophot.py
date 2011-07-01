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
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import os
import sqlite3
import tempfile
import unittest
#import uuid

# imports from third party modules
from flask import g
#from werkzeug.datastructures import FileStorage
#from werkzeug.datastructures import MultiDict
from werkzeug.exceptions import Unauthorized

# imports from this application
from ..app import app
from ..helpers import after_request
from ..helpers import before_request
from ..helpers import connect_db
from ..helpers import init_db
from ..helpers import get_last_display_position
from ..helpers import require_logged_in
from ..helpers import select_single
from ..helpers import select_single_row
from .helpers import TestSupport
from .helpers import temp_photos


class OphotTestCase(TestSupport):
    """Test class for the __init__ module in the ophot package."""

    # def test_add_new_category(self):
    #     """Test for adding a new category to the database."""
    #     with app.test_request_context('/'):
    #         before_request()
    #         categories = get_categories()
    #         new_id = add_new_category('foobar')
    #         new_categories = get_categories()
    #         self.assertNotIn(new_id, categories)
    #         self.assertEqual(max(categories) + 1, new_id)
    #         self.assertIn('foobar', new_categories.values())

    @unittest.expectedFailure
    def test_after_request(self):
        """Tests that the database is disconnected on each response from the
        server.

        """
        # assert that the connection is closed somehow? maybe try to close it
        # twice and catch the error
        self.fail('Not yet implemented.')

    def test_before_request(self):
        """Tests that the database object is connected on the Flask global
        object before each request.

        """
        with app.test_request_context('/'):
            before_request()
            self.assertIsInstance(g.db, sqlite3.Connection)

    def test_connect_db(self):
        """Tests that the ophot module correctly connects to a database."""
        try:
            conn = connect_db()
            cursor = conn.execute('select *  from photo')
            self.assertEqual(0, len(cursor.fetchall()))
            cursor = conn.execute('select * from category')
            rows = cursor.fetchall()
            self.assertEqual('landscape', rows[0][1])
            self.assertEqual('personal', rows[1][1])
            self.assertEqual('portrait', rows[2][1])
        finally:
            conn.close()

    # def test_get_categories(self):
    #     """Test for getting categories with their ID numbers."""
    #     with app.test_request_context('/'):
    #         before_request()
    #         categories = get_categories()
    #         self.assertIn((1, 'landscape'), categories.items())
    #         self.assertIn((2, 'personal'), categories.items())
    #         self.assertIn((3, 'portrait'), categories.items())

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
            self.assertEqual(0, len(cursor.fetchall()))
            cursor = conn.execute('select * from category')
            rows = cursor.fetchall()
            self.assertEqual('landscape', rows[0][1])
            self.assertEqual('personal', rows[1][1])
            self.assertEqual('portrait', rows[2][1])
        finally:
            if conn is not None:
                conn.close()

    @unittest.skip('The flask.session object does not seem to work here.')
    def test_require_logged_in(self):
        """Test for requiring that the user is marked as logged in on the
        session.

        """
        with app.test_request_context('/') as c:
            #before_request()
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

    def test_select_single_row(self):
        """Tests that the select_single function returns the first matched row
        of a query.

        """
        with app.test_request_context('/'):
            before_request()
            with temp_photos():
                photo = select_single_row('select * from photo'
                                          ' where photocategory=1')
                self.assertEqual(4, len(photo))
                photoid, pos, filename, category = photo
                self.assertEqual(1, photoid)
                self.assertEqual(2, pos)
                self.assertEqual('photo1', filename)
                self.assertEqual(1, category)
                photo = select_single_row('select * from photo'
                                          ' where photocategory=2')
                self.assertEqual(4, len(photo))
                photoid, pos, filename, category = photo
                self.assertEqual(3, photoid)
                self.assertEqual(1, pos)
                self.assertEqual('photo3', filename)
                self.assertEqual(2, category)
