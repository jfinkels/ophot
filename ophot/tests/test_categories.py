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
"""Unit tests for the categories module."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import json
import unittest

# imports from this application
from ophot.tests import TestSupport


class CategoriesTestCase(TestSupport):
    """Test case for the ophot.categories module."""

    def test_get_categories(self):
        """Test for getting all categories."""
        response = self.app.get('/categories')
        result = json.loads(response.data)
        categories = result['items']
        # categories should contain just the initial categories specified by
        # the schema first
        self.assertEqual(categories[0], dict(id=1, name='landscape'))
        self.assertEqual(categories[1], dict(id=2, name='personal'))
        self.assertEqual(categories[2], dict(id=3, name='portrait'))
        # categories should be in alphabetical order by name
        for i in range(len(categories) - 1):
            self.assertLessEqual(categories[i]['name'],
                                 categories[i + 1]['name'])

    def test_create_category(self):
        """Test for creating a new category by name."""
        self._login()
        response = self.app.post('/categories', data=dict(name='foo'))
        result = json.loads(response.data)
        # check that the response has the correct information
        self.assertEqual('foo', result['name'])
        self.assertEqual(4, result['id'])
        # check that the changes stuck with the database
        self._logout()
        response = self.app.get('/categories/4')
        result = json.loads(response.data)
        self.assertEqual('foo', result['name'])
        self.assertEqual(4, result['id'])

    def test_get_category(self):
        """Test for getting a category by ID."""
        response = self.app.get('/categories/1')
        result = json.loads(response.data)
        self.assertEqual('landscape', result['name'])
        self.assertEqual(1, result['id'])
        response = self.app.get('/categories/2')
        result = json.loads(response.data)
        self.assertEqual('personal', result['name'])
        self.assertEqual(2, result['id'])
        response = self.app.get('/categories/3')
        result = json.loads(response.data)
        self.assertEqual('portrait', result['name'])
        self.assertEqual(3, result['id'])

    def test_update_category_name(self):
        """Test for updating the name of a category."""
        self._login()
        response = self.app.post('/categories/1', data=dict(name='foo'))
        result = json.loads(response.data)
        # check that the response gives the correct name
        self.assertEqual('foo', result['name'])
        self.assertEqual(1, result['id'])
        # check that the changes were made in the database
        response = self.app.get('/categories/1')
        result = json.loads(response.data)
        self.assertEqual('foo', result['name'])
        self.assertEqual(1, result['id'])

    def test_delete_category(self):
        """Test for deleting a category."""
        self._login()
        response = self.app.delete('/categories/1')
        self.assertEqual(204, response.status_code)
        self.assertEqual('', response.data)
        # check that the changes were made in the database
        response = self.app.get('/categories/1')
        self.assertEqual(404, response.status_code)
