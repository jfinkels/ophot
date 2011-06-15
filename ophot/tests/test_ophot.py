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
import uuid

# imports from third party modules
from werkzeug.datastructures import FileStorage
from werkzeug.datastructures import MultiDict

# imports from this application
from ophot import add_new_category
from ophot import app
from ophot import after_request
from ophot import before_request
from ophot import connect_db
from ophot import get_categories
from ophot import init_db

class OphotTestCase(unittest.TestCase):
    """Test class for the ophot module."""

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

    def login(self, username=app.config['USERNAME'],
              password=app.config['PASSWORD']):
        """Makes a POST request to login to the Flask application with the
        specified username and password. If no username and password are
        specified, the ones from the configuration will be used.

        """
        return self.app.post('/login',
                             data={'username': username, 'password': password},
                             follow_redirects=True)

    def logout(self):
        """Logs out from the current application."""
        return self.app.get('/logout', follow_redirects=True)

    def testInitDB(self):
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

    def testConnectDB(self):
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

    # def testAllowedFile(self):
    #     """Test that allowed_file() accepts only certain image files."""
    #     good_names = ['1.jpg', '2.JPG', '3.png', '4.PNG', '5.jpeg', '6.JPEG']
    #     bad_names = ['1', '2.jpg.2', '3.txt', '']
    #     for name in good_names:
    #         self.assertTrue(allowed_file(name))
    #     for name in bad_names:
    #         self.assertFalse(allowed_file(name))

    # def testGenerateFilename(self):
    #     """Tests that generate_filename() generates a good random
    #     filename.

    #     """
    #     # good filename
    #     filename = generate_filename('/foo/bar', 'baz.jpg')
    #     self.assertTrue(filename.endswith('.jpg'))
    #     try:
    #         uuid.UUID(filename.split('.')[0])
    #     except ValueError:
    #         self.fail("Prefix of generated filename doesn't look like a UUID.")

    #def testBeforeRequest(self):
    #    """Tests that the database object is connected on the Flask global
    #    object before each request.

    #    """
    #    connection = connect_db()
    #    before_request()
    #    self.assertEqual(flask.g.db, connection)

    #def testAfterRequest(self):
    #    """Tests that the database is disconnected on each response from the
    #    server.

    #    """
    #    # assert that the connection is closed somehow? maybe try to close it
    #    # twice and catch the error
    #    self.fail('Not yet implemented.')

    # def testShowSplash(self):
    #     """Tests that the splash page shows up on requests for the index."""
    #     result = self.app.get('/')
    #     self.assertTrue(app.config['NAME'] in result.data)
    #     self.assertTrue('copyright' in result.data)

    # def testAddPhotos(self):
    #     """Tests that adding photos successfully commits them to the database.

    #     """
    #     result = self.app.get('/add')
    #     self.assertTrue('Only the administrator may add photos' in result.data)
    #     self.login()
    #     result = self.app.get('/add')
    #     self.assertTrue('upload one or more photos' in result.data)
    #     self.assertTrue('images will be scaled' in result.data)
    #     self.assertTrue('id="add-photo-form"' in result.data)
    #     self.logout()

    #     result = self.app.post('/add')
    #     self.assertTrue(result.status_code == 401)

    #     # TODO figure out how to send files through data
    #     #self.login()
    #     testfile = tempfile.TemporaryFile()
    #     filestorage = FileStorage(stream=testfile)
    #     multidict = MultiDict([('photos', filestorage)])

    #     result = self.app.post('/add', data={'photos': multidict,
    #                                                 'category': 1},
    #                            follow_redirects=True)
    #     self.fail('Not yet implemented')

    def testLogin(self):
        result = self.login()
        self.assertTrue('You have successfully logged in.' in result.data)
        result = self.logout()
        self.assertTrue('You have successfully logged out.' in result.data)
        result = self.login(username='bogus')
        self.assertTrue('Invalid username or password.' in result.data)
        result = self.login(password='bogus')
        self.assertTrue('Invalid username or password.' in result.data)

    def testLogout(self):
        result = self.login()
        self.assertTrue('You have successfully logged in.' in result.data)
        result = self.logout()
        self.assertTrue('You have successfully logged out.' in result.data)

    # def testGetPhotos(self):
    #     testfile1 = tempfile.mkstemp()
    #     testfile2 = tempfile.mkstemp()
    #     try:
    #         conn = connect_db()
    #         conn.execute('insert into photo (photofilename, photocategory,'
    #                      ' photodisplayposition) values (?, ?, ?)',
    #                      [testfile1[1], '1', '1'])
    #         conn.execute('insert into photo (photofilename, photocategory,'
    #                      ' photodisplayposition) values (?, ?, ?)',
    #                      [testfile2[1], '1', '2'])
    #         conn.commit()
            
    #         # TODO add some photos to the database
    #         result = self.app.get('/_get_photos', data = {'categoryid': 1},
    #                               follow_redirects=True)
    #         print result.data
    #         self.fail('Not yet implemented.')
    #     finally:
    #         conn.close()
    #         os.unlink(testfile1[1])
    #         os.unlink(testfile2[1])

    # def testDeletePhoto(self):
    #     """Tests that the /_delete_photo route deletes the requested photo from
    #     the database.

    #     """
    #     try:
    #         testfile = tempfile.mkstemp()
    #         conn = connect_db()
    #         conn.execute('insert into photo (photofilename, photocategory,'
    #                      ' photodisplayposition) values (?, ?, ?)',
    #                      [testfile[1], '1', '1'])
    #         conn.commit()
    #         result = self.app.delete('/_delete_photo', data = {'photoid': 1},
    #                                  follow_redirects=True)
    #         self.assertTrue(len(conn.execute('select * from photo').fetchall()) == 0)
            
    #     finally:
    #         conn.close()
    #         os.unlink(testfile[1])

    # def testPageNotFound(self):
    #     """Tests that requests to GET a bogus page result in a 404 which gets
    #     handled by the server.

    #     """
    #     result = self.app.get('/bogusurl', follow_redirects=True)
    #     self.assertTrue('Could not find the page you requested.'
    #                     in result.data)

def suite():
    """Returns the test suite which runs all tests in this module."""
    return unittest.TestLoader().loadTestsFromTestCase(OphotTestCase)
