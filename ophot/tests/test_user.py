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
import unittest

# imports from third-party modules
from configobj import ConfigObj

# imports from this application
from ophot import app
from ophot import site_config
from ophot.tests import TestSupport


class preserve_site_config:
    """Context manager (for use in a "with" statement) which stores the
    original configuration settings from a file on enter, and rewrites those
    settings on exit.

    """
    def __init__(self):
        """Does nothing."""
        pass

    def __enter__(self):
        """Reads the configuration settings file and stashes it so that it can
        be restored later.

        Returns a copy of the original config (in case calling code makes
        changes to this context manager).

        """
        self.original_config = ConfigObj(app.config['SETTINGS_FILE'])
        return ConfigObj(self.original_config)

    def __exit__(self, exception_type, exception_value, traceback):
        """Writes the original configuration settings back to the settings
        file.

        """
        self.original_config.write()

@unittest.skip('Skip until figure out how to get POST to work')
class UserTestCase(TestSupport):
    """Test class for the user module."""

    def test_get_user_settings(self):
        """Tests getting the user settings."""
        result = json.loads(self.app.get('/user').data)
        for name in result:
            self.assertEqual(site_config[name.upper()], result[name])

    def test_update_spacing(self):
        """Tests changing the spacing (in pixels) between photos on the splash
        page.

        """
        self._login()
        with preserve_site_config() as conf:
            response = self.app.post('/user', data='spacing=123', content_type='application/x-www-form-urlencoded')
            result = json.loads(response.data)
            self.assertEqual(conf['BIO'], result['bio'])
            self.assertEqual(conf['CONTACT'], result['contact'])
            self.assertEqual(123, result['spacing'])
            for name in result:
                self.assertEqual(site_config[name.upper()], result[name])
        # TODO test change spacing if no spacing exists yet

    def test_update_bio(self):
        """Test for updating bio information."""
        self._login()
        with preserve_site_config() as conf:
            result = json.loads(self.app.patch('/user', data=dict(bio='foo bar\nbaz')).data)
            
            self.assertEqual('foo bar\nbaz', result['bio'])
            self.assertEqual(conf['CONTACT'], result['contact'])
            self.assertEqual(conf['SPACING'], result['spacing'])
            for name in result:
                self.assertEqual(site_config[name.upper()], result[name])
        # TODO test bogus parameters

    def test_update_contact(self):
        """Test for updating bio information."""
        self._login()
        with preserve_site_config() as conf:
            result = json.loads(self.app.patch('/user', data=dict(bio='foo bar\nbaz')).data)
            
            self.assertEqual('foo bar\nbaz', result['bio'])
            self.assertEqual(conf['CONTACT'], result['contact'])
            self.assertEqual(conf['SPACING'], result['spacing'])
            for name in result:
                self.assertEqual(site_config[name.upper()], result[name])
        # TODO test bogus parameters

    def test_update_multiple(self):
        """Test for updating multiple user settings."""
        self._login()
        with preserve_site_config() as conf:
            result = json.loads(self.app.patch('/user', data=dict(bio='foo bar\nbaz', contact='hello')).data)
            
            self.assertEqual('foo bar\nbaz', result['bio'])
            self.assertEqual('hello', result['contact'])
            self.assertEqual(conf['SPACING'], result['spacing'])
            for name in result:
                self.assertEqual(site_config[name.upper()], result[name])
        # TODO test bogus parameters
