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

class ViewsTestCase(TestSupport):
    """Test class for the requests module."""

    def test_allowed_file(self):
        """Tests that only certain image file types are allowed."""
        self.fail('not yet implemented')

    def test_generate_filename(self):
        """Tests that filenames are correctly generated for uploaded photos."""
        self.fail('not yet implemented')

    def test_get_categories_plus_new(self):
        """Test for getting the names of all categories, plus the string
        'new...'.

        """
        self.fail('not yet implemented')

    def test_to_html_paragraphs(self):
        """Test for converting a multi-line string to sequence of HTML <p>
        blocks.

        """
        self.fail('not yet implemented')

    def test_add_photos_display(self):
        """Test for displaying the add photos page."""
        self.fail('not yet implemented')

    def test_add_photos_upload(self):
        """Test for uploading photos using the add photos page."""
        self.fail('not yet implemented')

    def test_change_splash_photo_display(self):
        """Test for displaying the change splash photo page."""
        self.fail('not yet implemented')

    def test_change_splash_photo_upload(self):
        """Test for uploading a new splash page photo using the change splash
        photo page.

        """
        self.fail('not yet implemented')

    def test_forbidden(self):
        """Test for the HTTP error 403 page."""
        self.fail('not yet implemented')

    def test_login_display(self):
        """Test that the login page is displayed correctly."""
        self.fail('not yet implemented')

    def test_login_credentials(self):
        """Test that logging in by providing a username and password works as
        expected.

        """
        self.fail('not yet implemented')

    def test_logout(self):
        """Tests that logging out works."""
        self.fail('not yet implemented')

    def test_page_not_found(self):
        """Tests that the HTTP error 404 page displays correctly."""
        self.fail('not yet implemented')

    def test_settings(self):
        """Tests that the settings page displays correctly."""
        self.fail('not yet implemented')

    def test_show_splash(self):
        """Tests that the splash page displays correctly."""
        self.fail('not yet implemented')
