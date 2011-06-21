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
"""Unit tests for the views module."""
import os.path
import tempfile
import unittest
import uuid

from ophot import app
from ophot import before_request
from ophot import get_categories
from ophot.tests import TestSupport
from ophot.views import _allowed_file
from ophot.views import _generate_filename
from ophot.views import _get_categories_plus_new
from ophot.views import _to_html_paragraphs
from ophot.views import add_photos
from ophot.views import change_splash_photo
from ophot.views import forbidden
from ophot.views import login
from ophot.views import logout
from ophot.views import page_not_found
from ophot.views import settings
from ophot.views import show_splash
from ophot.views import unauthorized


class ViewsTestCase(TestSupport):
    """Test class for the requests module."""

    def test_allowed_file(self):
        """Tests that only certain image file types are allowed."""
        good_names = ['1.jpg', '2.JPG', '3.png', '4.PNG', '5.jpeg', '6.JPEG']
        bad_names = ['1', '2.jpg.2', '3.txt', '']
        for name in good_names:
            self.assertTrue(_allowed_file(name))
        for name in bad_names:
            self.assertFalse(_allowed_file(name))

    def test_generate_filename(self):
        """Tests that filenames are correctly generated for uploaded photos."""
        filename = _generate_filename('/foo/bar', 'baz.jpg')
        self.assertTrue(filename.endswith('.jpg'))
        try:
            uuid.UUID(os.path.basename(filename).split('.')[0])
        except ValueError:
            self.fail("Prefix of generated filename doesn't look like a UUID.")

    def test_get_categories_plus_new(self):
        """Test for getting the names of all categories, plus the string
        'new...'.

        """
        with app.test_request_context('/'):
            before_request()
            categories = _get_categories_plus_new()
            self.assertIn((1, 'landscape'), categories)
            self.assertIn((2, 'personal'), categories)
            self.assertIn((3, 'portrait'), categories)
            self.assertIn((-1, 'new category...'), categories)

    def test_to_html_paragraphs(self):
        """Test for converting a multi-line string to sequence of HTML <p>
        blocks.

        """
        string = '''Paragraph 1
Paragraph 2

Paragraph 3
Paragraph 4
'''
        result = _to_html_paragraphs(string)
        self.assertIn('<p>Paragraph 1</p>', result)
        self.assertIn('<p>Paragraph 2</p>', result)
        self.assertIn('<p>Paragraph 3</p>', result)
        self.assertIn('<p>Paragraph 4</p>', result)

    def test_add_photos_display(self):
        """Test for displaying the add photos page."""
        result = self.app.get('/add')
        self.assertIn('Only the administrator may add photos', result.data)
        self._login()
        result = self.app.get('/add')
        self.assertIn('upload one or more photos', result.data)
        self.assertIn('images will be scaled', result.data)
        self.assertIn('id="add-photo-form"', result.data)

    @unittest.expectedFailure
    def test_add_photos_upload(self):
        """Test for uploading photos using the add photos page."""
        # TODO figure out how to send files through data
        #self.login()
        #testfile = tempfile.TemporaryFile()
        #result = self.app.post('/add', data={'photos': testfile,
        #                                     'category': 1},
        #                       follow_redirects=True)
        self.fail('Not yet implemented')

    def test_change_splash_photo_display(self):
        """Test for displaying the change splash photo page."""
        result = self.app.get('/change_splash_photo')
        self.assertIn('Only the administrator', result.data)
        self.assertNotIn('id="photo-upload-form"', result.data)
        self._login()
        result = self.app.get('/change_splash_photo')
        self.assertNotIn('Only the administrator', result.data)
        self.assertIn('id="photo-upload-form"', result.data)
        self.assertIn(str(app.config['SPLASH_PHOTO_WIDTH']), result.data)
        self.assertIn(str(app.config['SPLASH_PHOTO_HEIGHT']), result.data)

    @unittest.expectedFailure
    def test_change_splash_photo_upload(self):
        """Test for uploading a new splash page photo using the change splash
        photo page.

        """
        # TODO figure out how to send files through data
        self.fail('not yet implemented')

    @unittest.expectedFailure
    def test_forbidden(self):
        """Test for the HTTP error 403 page."""
        # TODO figure out how to trigger an HTTP error 403
        self.fail('not yet implemented')

    def test_login_display(self):
        """Test that the login page is displayed correctly."""
        result = self.app.get('login')
        self.assertIn('username', result.data)
        self.assertIn('password', result.data)
        self.assertIn('id="login-form"', result.data)

    def test_login_credentials(self):
        """Test that logging in by providing a username and password works as
        expected.

        """
        result = self._login()
        self.assertIn('You have successfully logged in.', result.data)
        result = self._logout()
        self.assertIn('You have successfully logged out.', result.data)
        result = self._login(username='bogus')
        self.assertIn('Invalid username or password.', result.data)
        result = self._login(password='bogus')
        self.assertIn('Invalid username or password.', result.data)

    def test_logout(self):
        """Tests that logging out works."""
        result = self._login()
        self.assertIn('You have successfully logged in.', result.data)
        result = self._logout()
        self.assertIn('You have successfully logged out.', result.data)

    def test_page_not_found(self):
        """Tests that the HTTP error 404 page displays correctly."""
        result = self.app.get('/bogusurl', follow_redirects=True)
        self.assertIn('Could not find the page you requested.', result.data)

    def test_settings_display(self):
        """Tests that the settings page displays correctly."""
        self._login()
        result = self.app.get('/settings')
        self.assertIn('configuration for the site', result.data)
        self.assertIn('id="settings-table"', result.data)
        with app.test_request_context():
            before_request()
            for categoryname in get_categories().values():
                self.assertIn(categoryname, result.data)

    def test_show_splash(self):
        """Tests that the splash page displays correctly."""
        result = self.app.get('/')
        self.assertIn(app.config['NAME'], result.data)
        self.assertIn('copyright', result.data)

    def test_unauthorized(self):
        """Test for the HTTP error 401 page."""
        result = self.app.delete('/delete/1')
        self.assertEqual(401, result.status_code)
        self.assertIn('not authorized', result.data)
