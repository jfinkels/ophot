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
"""Unit tests for the _rest module."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import json

# imports from this application
from .. import app
from .._rest import jsonify_status_code
from .._rest import to_category_dict
from .._rest import to_photo_dict
from . import TestSupport


class RestTestCase(TestSupport):
    """Test case for the ophot._rest module."""

    def test_jsonify_status_code(self):
        """Test for getting creating a jsonified response with a specific
        status_code.

        """
        with app.test_request_context('/'):
            response = jsonify_status_code(404, foo='bar')
            self.assertEqual(404, response.status_code)
            self.assertIn('foo', json.loads(response.data))
            self.assertEqual('bar', json.loads(response.data)['foo'])

    def test_to_category_dict(self):
        """Test for converting a database row into a dictionary representing
        the state of a category.

        """
        db_row = [1, 'foo']
        result = to_category_dict(db_row)
        self.assertIn('id', result)
        self.assertIn('name', result)
        self.assertEqual(1, result['id'])
        self.assertEqual('foo', result['name'])

    def test_to_category_dict(self):
        """Test for converting a database row into a dictionary representing
        the state of a photo.

        """
        db_row = [1, 2, 'foo', 3]
        result = to_photo_dict(db_row)
        self.assertIn('id', result)
        self.assertIn('displayposition', result)
        self.assertIn('filename', result)
        self.assertIn('categoryid', result)
        self.assertEqual(1, result['id'])
        self.assertEqual(2, result['displayposition'])
        self.assertEqual('foo', result['filename'])
        self.assertEqual(3, result['categoryid'])
