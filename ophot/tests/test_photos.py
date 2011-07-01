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
"""Unit tests for the photos module."""
# imports for compatibility with future python versions
from __future__ import absolute_import
from __future__ import division

# imports from built-in modules
import json

# imports from this application
from .helpers import temp_photos
from .helpers import TestSupport


# TODO override setUp() and tearDown() in this class to just do whatever with
# temp_photos() does
class PhotosTestCase(TestSupport):
    """Test case for the ophot.photos module."""

    def test_get_photo(self):
        """Test for getting a single photo."""
        with temp_photos():
            response = self.app.get('/photos/1')
            result = json.loads(response.data)
            self.assertEqual(1, result['id'])
            self.assertEqual(2, result['displayposition'])
            self.assertEqual('photo1', result['filename'])
            self.assertEqual(1, result['categoryid'])
            response = self.app.get('/photos/2')
            result = json.loads(response.data)
            self.assertEqual(2, result['id'])
            self.assertEqual(1, result['displayposition'])
            self.assertEqual('photo2', result['filename'])
            self.assertEqual(1, result['categoryid'])
            response = self.app.get('/photos/3')
            result = json.loads(response.data)
            self.assertEqual(3, result['id'])
            self.assertEqual(1, result['displayposition'])
            self.assertEqual('photo3', result['filename'])
            self.assertEqual(2, result['categoryid'])
            response = self.app.get('/photos/4')
            self.assertEqual(404, response.status_code)

    def test_get_photos(self):
        """Test for getting all photos."""
        with temp_photos():
            response = self.app.get('/photos')
            result = json.loads(response.data)
            self.assertIn('items', result)
            self.assertEqual(3, len(result['items']))

    def test_get_photos_by_category(self):
        """Tests for getting photos by category."""
        with temp_photos():
            # test for a category with two photos
            response = self.app.get('/photos/by-category/1')
            result = json.loads(response.data)
            self.assertIn('items', result)
            self.assertEqual(2, len(result['items']))
            # test for a category with one photo
            response = self.app.get('/photos/by-category/2')
            result = json.loads(response.data)
            self.assertIn('items', result)
            self.assertEqual(1, len(result['items']))
            # test for a category with no photos
            response = self.app.get('/photos/by-category/3')
            result = json.loads(response.data)
            self.assertIn('items', result)
            self.assertEqual(0, len(result['items']))
            # TODO test for a category which doesn't exist
            #response = self.app.get('/photos/by-category/4')
            #self.assertEqual(404, response.status_code)

    def test_update_photo_displayposition(self):
        """Test for changing the category of a photo."""
        self._login()
        with temp_photos():
            response = self.app.post('/photos/1', data=dict(displayposition=3))
            result = json.loads(response.data)
            # check that the response has the correct information
            self.assertEqual(1, result['id'])
            self.assertEqual('photo1', result['filename'])
            self.assertEqual(3, result['displayposition'])
            self.assertEqual(1, result['categoryid'])
            # check that the correct information is in the database
            response = self.app.get('/photos/1')
            result = json.loads(response.data)
            self.assertEqual(1, result['id'])
            self.assertEqual('photo1', result['filename'])
            self.assertEqual(3, result['displayposition'])
            self.assertEqual(1, result['categoryid'])

    def test_update_photo_category(self):
        """Test for changing the category of a photo."""
        self._login()
        with temp_photos():
            response = self.app.post('/photos/1', data=dict(categoryid=3))
            result = json.loads(response.data)
            # check that the response has the correct information
            self.assertEqual(1, result['id'])
            self.assertEqual('photo1', result['filename'])
            # updated to 1 + last photo position
            self.assertEqual(1, result['displayposition'])
            self.assertEqual(3, result['categoryid'])
            # check that the correct information is in the database
            response = self.app.get('/photos/1')
            result = json.loads(response.data)
            self.assertEqual(1, result['id'])
            self.assertEqual('photo1', result['filename'])
            self.assertEqual(1, result['displayposition'])
            self.assertEqual(3, result['categoryid'])
            # each category should have just one photo now
            for categoryid in (1, 2, 3):
                route = '/photos/by-category/{0}'.format(categoryid)
                response = self.app.get(route)
                result = json.loads(response.data)
                self.assertEqual(1, len(result['items']))
        # TODO test changing category of a photo which doesn't exist
        # TODO test changing to a category which doesn't exist

    def test_update_photo_bad_request(self):
        """Tests for requests which attempt to update both the category and the
        displayposition of a photo.

        """
        self._login()
        with temp_photos():
            response = self.app.post('/photos/1', data=dict(categoryid=3,
                                                            displayposition=5))
            self.assertEqual(400, response.status_code)

    def test_delete_photo(self):
        """Test for deleting a photo from the database."""
        self._login()
        with temp_photos():
            response = self.app.delete('/photos/1')
            self.assertEqual(204, response.status_code)
            self.assertEqual('', response.data)
            # check that the changes were made in the database
            response = self.app.get('/photos/1')
            self.assertEqual(404, response.status_code)
        # TODO test deleting a photo which does not exist
