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
"""Unit tests for the user module."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import json
import os
import tempfile
import unittest

# imports from this application
from ..app import app
from ..app import site_config
from .helpers import TestSupport


class preserve_site_config(object):
    """Context manager (for use in a "with" statement) which makes the
    ophot.site_config object write changes to a temporary file while in the
    context, then reloads the original configuration on exit.

    """

    def __enter__(self):
        """Makes the ophot.site_config object use a temporary file for changes
        made within this context.

        """
        # create a temp file for the site_config where changes will be written
        self.fd, self.filename = tempfile.mkstemp()
        # write the contents of the current site_config to the temp file
        site_config.filename = self.filename
        site_config.write()

    def __exit__(self, exception_type, exception_value, traceback):
        """Reloads the original configuration back into ophot.site_config."""
        # delete the temporary file
        os.close(self.fd)
        os.unlink(self.filename)
        # reload the original site_config information
        site_config.filename = app.config['SETTINGS_FILE']
        site_config.reload()


class UserTestCase(TestSupport):
    """Test class for the user module."""

    def _assert_config_matches(self, result):
        """Asserts that all configuration key/value pairs in the specified JSON
        response match the expected values in the corresponding site_config
        key/value pairs.

        """
        for name in result:
            self.assertEqual(site_config[name.upper()], result[name])

    def test_get_user_settings(self):
        """Tests getting the user settings."""
        result = json.loads(self.app.get('/user').data)
        self._assert_config_matches(result)

    def test_update_spacing(self):
        """Tests changing the spacing (in pixels) between photos on the splash
        page.

        """
        self._login()
        with preserve_site_config():
            response = self.app.post('/user', data=dict(spacing=123))
            result = json.loads(response.data)
            self._assert_config_matches(result)
            self.assertEqual(123, result['spacing'])
        # TODO test change spacing if no spacing exists yet

    def test_update_bio(self):
        """Test for updating bio information."""
        self._login()
        with preserve_site_config() as conf:
            response = self.app.post('/user', data=dict(bio='foo bar\nbaz'))
            result = json.loads(response.data)
            self._assert_config_matches(result)
            self.assertEqual('foo bar\nbaz', result['bio'])
        # TODO test bogus parameters

    def test_update_contact(self):
        """Test for updating contact information."""
        self._login()
        with preserve_site_config() as conf:
            response = self.app.post('/user', data=dict(contact='foobar'))
            result = json.loads(response.data)
            self._assert_config_matches(result)
            self.assertEqual('foobar', result['contact'])
        # TODO test bogus parameters

    def test_update_multiple(self):
        """Test for updating multiple user settings."""
        self._login()
        with preserve_site_config():
            response = self.app.post('/user', data=dict(bio='foo bar\nbaz',
                                                        contact='hello'))
            result = json.loads(response.data)
            self._assert_config_matches(result)
            self.assertEqual('foo bar\nbaz', result['bio'])
            self.assertEqual('hello', result['contact'])
        # TODO test bogus parameters
